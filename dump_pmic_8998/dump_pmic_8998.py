import subprocess
import time
import getopt, sys

ldo_range = 0x100
ldo_max_count = 28
ldo_base = 0x4000
ldo_count = ldo_range * ldo_max_count

lvs_range = 0x100
lvs_max_count = 2
lvs_base = 0x8000
lvs_count = ldo_range * lvs_max_count

smps_range = 0x300
smps_max_count = 13
smps_base = 0x1400
smps_count = smps_range * smps_max_count

pmk_smps_range = 0x300
pmk_smps_max_count = 4
pmk_smps_base = 0x1400
pmk_smps_count = pmk_smps_range * pmk_smps_max_count

bob_range = 0x100
bob_max_count = 1
bob_base = 0xA000
bob_count = bob_range * bob_max_count

bob_mon_range = 0x100
bob_mon_max_count = 1
bob_mon_base = 0xA100
bob_mon_count = bob_mon_range * bob_mon_max_count

pmic_sid_name = {	0: 'PM',
			1: 'PM',
			2: 'PMI',
                        3: 'PMI',
			4: 'PMK',
			5: 'PMK'}

info_offset = [0x04, 0x05, 0x08, 0x42, 0x43, 0x48]
info_offset_def = [	'type',		# 0x04
			'subtype',	# 0x05
			'status1',	# 0x08
			'vset_lb_valid',# 0x42
			'vset_ub_valid',# 0x43
			'pd_ctl']	# 0x48

bob_info_offset = [ 0x04, 0x05, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x42, 0x43, 0x48]
bob_info_offset_def = [	'type',		# 0x04
			'subtype',	# 0x05
			'status1',	# 0x08
			'status2',	# 0x09
			'status3',	# 0x0A
			'status4',	# 0x0B
			'status5',	# 0x0C
			'vset_lb_valid',# 0x42
			'vset_ub_valid',# 0x43
			'pd_ctl']	# 0x48

info_def = zip(info_offset, info_offset_def)

info_type = {	 1: 'PON',
		 2: 'CHARGER',
		 3: 'HF_',
		 4: 'LDO',
		 5: 'VS',
		 6: 'CLOCK',
		 7: 'RTC',
		 8: 'ADC',
		 9: 'ALARM',
		10: 'INTERRUPT',
		11: 'INTERFACE',
		12: 'TRIM',
		13: 'FG',
		14: 'MBG',
		15: 'LED_DRIVER',
		16: 'GPIO',
		17: 'MPP',
		18: 'KEYPAD',
		19: 'LPG',
		20: 'MISC',
		21: 'HAPTICS',
		22: 'PBS',
		23: 'WLED',
		24: 'FLASH',
		25: 'RGB',
		26: 'KEYPAD_BL',
		27: 'BOOST',
		28: 'FT_',
		29: 'BUCK_CMN',
		31: 'BOOST_BYP',
		33: 'ULT_LDO',
		34: 'ULT_BUCK',
		41: 'BOB' }

ldo_info_subtype = { 	 1: 'N50        ',
			 2: 'N150       ',
			 3: 'N300       ',
			 4: 'N600       ',
			 5: 'N1200      ',
			 6: 'N600_ST    ',
			 7: 'N1200_ST   ',
			 8: 'P50        ',
			 9: 'P150       ',
			10: 'P300       ',
			11: 'P600       ',
			12: 'P1200      ',
			16: 'LN_LDO     ',
			24: 'USB_LDO    ',
			40: 'LV_P50     ',
			41: 'LV_P150    ',
			42: 'LV_P300    ',
			43: 'LV_P600    ',
			44: 'LV_P1200   ',
			48: 'HT_N300_ST ',
			49: 'HT_N600_ST ',
			50: 'HT_N1200_ST',
			52: 'HT_P50     ',
			53: 'HT_P150    ',
			54: 'HT_P300    ',
			55: 'HT_P600    ',
			56: 'HT_P1200   ',
			58: 'HT_LV_P50  ',
			59: 'HT_LV_P150 ',
			60: 'HT_LV_P300 ',
			61: 'HT_LV_P600 ',
			62: 'HT_LV_P1200',
			64: 'HT_P50_SP  '}

vs_info_subtype = {	 1: 'LV100      ',
			 2: 'LV300      ',
			 8: 'MV300      ',
			 9: 'MV500      ',
			16: 'HDMI       ',
			17: 'OTG        '}

smps_info_subtype = {	 1: 'PS1X       ',
			 2: 'PS2X       ',
			 3: 'PS3X       ',
			 6: 'PS6X       ',
			 8: 'GP_CTL     ',
			 9: 'RF_CTL     ',
			10: 'PWM        '}

bob_info_subtype = { 	 3: 'CONF       ',
			 4: 'MON        ' }

def cal_voltage(lb, ub):
	return long(((ub & 0x0f)<< 8) + lb);

def bob_cal_voltage(status):
	return status*32

def parse_pd_ctl(pd_ctl, status):
	ret = ""
	if status & 0x80:
		if pd_ctl & 0x80: ret = ret + "PD,"
		if pd_ctl & 0x40: ret = ret + "PD(weak),"
		if pd_ctl & 0x20: ret = ret + "PD(leak),"
	return ret;

def parse_info_status(reg_type, status):
	ret = "|"
	if reg_type == 'LDO' or reg_type == 'FT_SMPS' or reg_type == 'HF_SMPS':
		if status & 0x80: ret = ret + "OK|"
		if status & 0x40: ret = ret + "ERR|"
		if status & 0x20: ret = ret + "OCP|"
		if status & 0x10: ret = ret + "NPM|"
		elif status & 0x80: ret = ret + "AUTO|"
		if status & 0x08: ret = ret + "BYP|"
		if status & 0x04: ret = ret + "STEP_DONE|"
	
	if reg_type == 'VS':
		if status & 0x80: ret = ret + "OK|"
		if status & 0x40: ret = ret + "OCP|"
		if status & 0x02: ret = ret + "NPM|"

	# ret = ret + "(0x%X)" % status
	return ret;

def parse_bob_info_status(subtype, s1, s2, s3, s5):
	ret = "|"
	#if subtype == 3:
	if s1 & 0x10: ret = ret + "OK|"
	if s1 & 0x40: ret = ret + "ERR|"
	if s1 & 0x80: ret = ret + "READY|"
	if s1 & 0x20: ret = ret + "FAULT|"
	if s1 & 0x08: ret = ret + "PASS|"
	if s1 & 0x04: ret = ret + "STEP_DONE|"
	if s1 & 0x02: ret = ret + "OVP|"
	if s1 & 0x01: ret = ret + "OT|"

	if s2 & 0x08: ret = ret + "PFM|"
	else: ret = ret + "PWM|"
	if s2 & 0x04: ret = ret + "THER_OVER|"
	if s2 & 0x02: ret = ret + "BULK|"
	if s2 & 0x01: ret = ret + "BST|"

	if s3 & 0x80: ret = ret + "COM|"
	if s3 & 0x40: ret = ret + "AUTO|"
	if s3 & 0x20: ret = ret + "H2|"
	if s3 & 0x10: ret = ret + "H1|"
	if s3 & 0x08: ret = ret + "H0|"
	if s3 & 0x04: ret = ret + "H2L|"
	if s3 & 0x02: ret = ret + "H1L|"
	if s3 & 0x01: ret = ret + "H0L|"

	if s5 & 0x20: ret = ret + "LMH2|"
	if s5 & 0x10: ret = ret + "LMH1|"
	if s5 & 0x08: ret = ret + "LMH0|"

	return ret;

def parse_info_subtype(reg_type, subtype):
	ret = ''
	if reg_type == 'LDO': ret = ldo_info_subtype[subtype]
	elif reg_type == 'VS': ret = vs_info_subtype[subtype]
	elif reg_type == 'FT_SMPS' or reg_type == 'HF_SMPS': ret = smps_info_subtype[subtype]
	elif reg_type == 'BOB': ret = bob_info_subtype[subtype]
	else: ret = int(subtype)
	return ret;

def check_reg_type(reg_type):
	ret = info_type[reg_type]
	if ret == 'FT_' or ret == 'HF_': ret = ret + 'SMPS'
	return ret;

def parse_info_iter(sid, index, info):
	reg_type = check_reg_type(info['type'])
	reg_subtype = info['subtype']
	
	if reg_type == 'BOB':
		reg_status = parse_bob_info_status(reg_subtype, info['status1'], info['status2'], info['status3'], info['status5'])
	else:
		reg_status = parse_info_status(reg_type, info['status1'])
	
	reg_pd = info['pd_ctl']
	if reg_type == "BOB":
		if reg_subtype == 3: reg_voltage = bob_cal_voltage(info['status4'])
		elif reg_subtype == 4: reg_voltage = 0
	else: reg_voltage = cal_voltage(info['vset_lb_valid'], info['vset_ub_valid'])

	if reg_voltage > 0:
            print "%s_%s_%d \t (%s): %4d mV\t %s :%s" % ( pmic_sid_name[sid],
					reg_type,
					(index + 1), 
					parse_info_subtype(reg_type, reg_subtype),
					reg_voltage,
					reg_status,
					parse_pd_ctl(reg_pd, info['status1']))
	else:
            print "%s_%s_%d \t (%s): %4d mV\t %s :%s" % ( pmic_sid_name[sid],
					reg_type,
					(index + 1), 
					parse_info_subtype(reg_type, reg_subtype),
					reg_voltage,
					reg_status,
					parse_pd_ctl(reg_pd, info['status1']))
	return;

def parse_info(sid, mylist, parse_list):
	for i, info in enumerate(mylist):
		if not parse_list:
			parse_info_iter(sid, i, info)
		elif i + 1 in (parse_list):
			parse_info_iter(sid, i, info)
	return;


pm_ldo_list = []
pm_lvs_list = []
pm_smps_list = []
pmk_smps_list = []
pmi_bob_list = []
pmi_bob_mon_list = []

def get_info_from_spmi(sid, base, count, reg_range, is_bob):
	curr_index = 0
	prev_index = 0
	mylist = []
	info = {}
	
	if is_bob:
		target_offset = bob_info_offset
		target_offset_def = bob_info_offset_def
	else:
		target_offset = info_offset
		target_offset_def = info_offset_def
	
	command_addr = "adb shell \"echo 0x%x > /d/regmap/spmi0-0%d/address\"" % (base, sid)
	# Read 3 more to make sure data should be updated properly
	command_cnt = "adb shell \"echo 0x%x > /d/regmap/spmi0-0%d/count\"" % (count + 3, sid)
	command_data = "adb shell cat /d/regmap/spmi0-0%d/data" % sid

	subprocess.call(command_addr, shell=True)
	subprocess.call(command_cnt, shell=True)
	
	proc = subprocess.Popen(command_data, shell=True, stdout=subprocess.PIPE)

	while True:
		line = proc.stdout.readline()
		if line != '':
			addr, data = line.split(":")
			addr = int(addr, 16)
			if addr < base + count: data = int(data, 16)
			
			if addr <= base + count:
				curr_index = (addr - base) / reg_range
				curr_offset = (addr - base) % reg_range
				if curr_index != prev_index:
					prev_index = curr_index
					mylist.append(info)
					info = {}
				
				if curr_offset in target_offset:
					key = target_offset_def[target_offset.index(curr_offset)]
					info[key] = data
			else:
				break	
	return mylist;

parse_all = False
parse_pmk = False
parse_pmk_list = []
parse_ldo = False
parse_ldo_list = []
parse_smps = False
parse_smps_list = []
parse_lvs = False
parse_bob = False

def usage():
	print "Usage:"
	print "\t-h               print this help"
	print "\t-a               print all list (default)"
	print "\t-l               print all PM_LDO"
	print "\t-L ldo1,ldo2,... print specified PM_LDO. Such as \"-L 1,13,27\" will only print PM_LDO_1, PM_LDO_13, PM_LDO_27"
	print "\t-s               print all PM_SMPS"
	print "\t-S smp1,smp2,... print specified PM_SMPS. such as \"-S 10,13\" will only print PM_SMPS_10, PM_SMPS_13"
	print "\t-b               print all PMI_BOB (config and monitor)"
	print "\t-v               print all PM_LVS"
	print "\t-k               print all PMK_SMPS"
	print "\t-K smp1,smp2,... print specified PMK_SMPS. such as \"-K 1\" will only print PMK_SMPS_1"
	return;

# __MAIN__
#com_root = "adb root"
#subprocess.call(com_root, shell=True)
#time.sleep(1)

if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:], "halL:sS:vbkK:i")
	except getopt.GetoptError as err:
		print err
		sys.exit(2)
	
	if not opts:
		parse_all = True;
	else:
		for o, a in opts:
			if o == "-h": usage()
			elif o == "-a": parse_all = True
			else:
				if o == "-k": parse_pmk = True
				if o == "-K":
					parse_pmk = True
					parse_pmk_list = map(int, a.split(','))
				if o == "-s": parse_smps = True
				if o == "-S":
					parse_smps = True
					parse_smps_list = map(int, a.split(','))
				if o == "-l": parse_ldo = True
				if o == "-L": 
					parse_ldo = True
					parse_ldo_list = map(int, a.split(','))
				if o == "-b": parse_bob = True
				if o == "-v": parse_lvs = True


if parse_all or parse_ldo:
	# Dump PM8998 LDO info.
	pm_ldo_list = get_info_from_spmi(1, ldo_base, ldo_count, ldo_range, False)
	parse_info(1, pm_ldo_list, parse_ldo_list)


if parse_all or parse_lvs:
	# Dump PM8998 LVS info
	pm_lvs_list = get_info_from_spmi(1, lvs_base, lvs_count, lvs_range, False)
	parse_info(1, pm_lvs_list, None)


if parse_all or parse_smps:
	# Dump PM8998 SMPS info
	pm_smps_list = get_info_from_spmi(1, smps_base, smps_count, smps_range, False)
	parse_info(1, pm_smps_list, parse_smps_list)


if parse_all or parse_pmk:
	# Dump PMK8005 SMPS info
	pmk_smps_list = get_info_from_spmi(5, pmk_smps_base, pmk_smps_count, pmk_smps_range, False)
	parse_info(5, pmk_smps_list, parse_pmk_list)

if parse_all or parse_bob:
	# PMI8998 BOB info
	pmi_bob_list = get_info_from_spmi(3, bob_base, bob_count, bob_range, True)
	parse_info(3, pmi_bob_list, None)

if parse_all or parse_bob:
	# PMI8998 BOB monitor infor
	pmi_bob_mon_list = get_info_from_spmi(3, bob_mon_base, bob_mon_count, bob_mon_range, True)
	parse_info(3, pmi_bob_mon_list, None)

# __END__

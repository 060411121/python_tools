import subprocess
import time
import getopt, sys

cpu_idle_bak = 0
cpu_total_bak = 0
cpu0_idle_bak = 0
cpu0_total_bak = 0
cpu1_idle_bak = 0
cpu1_total_bak = 0
cpu2_idle_bak = 0
cpu2_total_bak = 0
cpu3_idle_bak = 0
cpu3_total_bak = 0
cpu4_idle_bak = 0
cpu4_total_bak = 0
cpu5_idle_bak = 0
cpu5_total_bak = 0
cpu6_idle_bak = 0
cpu6_total_bak = 0
cpu7_idle_bak = 0
cpu7_total_bak = 0

def parse_info(cpu, idle, total):
    global cpu_idle_bak
    global cpu_total_bak
    global cpu0_idle_bak
    global cpu0_total_bak
    global cpu1_idle_bak
    global cpu1_total_bak
    global cpu2_idle_bak
    global cpu2_total_bak
    global cpu3_idle_bak
    global cpu3_total_bak
    global cpu4_idle_bak
    global cpu4_total_bak
    global cpu5_idle_bak
    global cpu5_total_bak
    global cpu6_idle_bak
    global cpu6_total_bak
    global cpu7_idle_bak
    global cpu7_total_bak
    if cmp(cpu, "cpu") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu_idle_bak), (total-cpu_total_bak))
        print "%2d%%," %(100 - (idle-cpu_idle_bak)*100/(total-cpu_total_bak)),
        cpu_idle_bak = idle
        cpu_total_bak = total
    if cmp(cpu, "cpu0") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu0_idle_bak), (total-cpu0_total_bak))
        print "%2d%%," %(100 - (idle-cpu0_idle_bak)*100/(total-cpu0_total_bak)),
        cpu0_idle_bak = idle
        cpu0_total_bak = total
    if cmp(cpu, "cpu1") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu1_idle_bak), (total-cpu1_total_bak))
        print "%2d%%," %(100 - (idle-cpu1_idle_bak)*100/(total-cpu1_total_bak)),
        cpu1_idle_bak = idle
        cpu1_total_bak = total
    if cmp(cpu, "cpu2") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu2_idle_bak), (total-cpu2_total_bak))
        print "%2d%%," %(100 - (idle-cpu2_idle_bak)*100/(total-cpu2_total_bak)),
        cpu2_idle_bak = idle
        cpu2_total_bak = total
    if cmp(cpu, "cpu3") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu3_idle_bak), (total-cpu3_total_bak))
        print "%2d%%," %(100 - (idle-cpu3_idle_bak)*100/(total-cpu3_total_bak)),
        cpu3_idle_bak = idle
        cpu3_total_bak = total
    if cmp(cpu, "cpu4") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu4_idle_bak), (total-cpu4_total_bak))
        print "%2d%%," %(100 - (idle-cpu4_idle_bak)*100/(total-cpu4_total_bak)),
        cpu4_idle_bak = idle
        cpu4_total_bak = total
    if cmp(cpu, "cpu5") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu5_idle_bak), (total-cpu5_total_bak))
        print "%2d%%," %(100 - (idle-cpu5_idle_bak)*100/(total-cpu5_total_bak)),
        cpu5_idle_bak = idle
        cpu5_total_bak = total
    if cmp(cpu, "cpu6") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu6_idle_bak), (total-cpu6_total_bak))
        print "%2d%%," %(100 - (idle-cpu6_idle_bak)*100/(total-cpu6_total_bak)),
        cpu6_idle_bak = idle
        cpu6_total_bak = total
    if cmp(cpu, "cpu7") == 0:
#        print "<%s: %d, %d>" %(cpu, (idle-cpu7_idle_bak), (total-cpu7_total_bak))
        print "%2d%%" %(100 - (idle-cpu7_idle_bak)*100/(total-cpu7_total_bak)),
        cpu7_idle_bak = idle
        cpu7_total_bak = total

    return;


def get_info_from_adb():
	curr_index = 0
	prev_index = 0
	info = {}
	
	command_data = "adb shell cat /proc/stat | grep cpu"

	proc = subprocess.Popen(command_data, shell=True, stdout=subprocess.PIPE)

	while True:
		line = proc.stdout.readline()
		if line != '':
			cpu , other = line.split(" ", 1)
                        if cmp(cpu[0:2], "cpu"[0:2]) == 0:
                            if cmp(cpu, "cpu") == 0:
                                dummy, other = other.split(" ", 1) 
			    user, nice, kernel, idle, iowait, irq, softirq, dummy = other.split(" ", 7)
                            # print "<%s: %s, %s, %s, %s, %s, %s, %s>" %(cpu, user, nice, kernel, idle, iowait, irq, softirq)
                            user = int(user)
                            nice = int(nice)
                            kernel = int(kernel)
                            idle = int(idle)
                            iowait = int(iowait)
                            irq = int(irq)
                            softirq = int(softirq)
                            total = user + nice + kernel + idle + iowait + irq +softirq
                #            print "<%s: %8d, %8d, %8d, %8d, %8d, %8d, %8d == total=%8d>" %(cpu, user, nice, kernel, idle, iowait, irq, softirq, total)
                            parse_info(cpu, idle, total)
                else:
                        print ""
                        break
	return ;

parse_all = False

def usage():
	print "Usage:"
	print "\t-h               print this help"
	print "\t-a               print all list (default)"
	print "\t-t               print speed"
	print "\t-s               print total number"
        print "\texample: xxx.py -t 2 -s 3"
	return;

# __MAIN__
#com_root = "adb root"
#subprocess.call(com_root, shell=True)
#time.sleep(1)

if __name__ == "__main__":
        sample = 10000000
        time_sleep = 1
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hals:f:vbkt:i")
	except getopt.GetoptError as err:
		print err
		sys.exit(2)
	
	if not opts:
		parse_all = True;
	else:
		for o, a in opts:
           #         print "%s   %s" %(o,a)
		    if o == "-h": usage()
                    elif o == "-a": parse_all = True
                    else:
			if o == "-t":
                            time_sleep = int(a)
                            parse_all = True;
			if o == "-s":
                            sample = int(a)
                            parse_all = True;




if parse_all:
	# Dump PM8998 LDO info.
        print "%19s, cpu,cpu0,cpu1,cpu2,cpu3,cpu4,cpu5,cpu6,cpu7" %"time"
        for i in range(0, sample):
            print time.strftime('%Y-%m-%d %H:%M:%S,',time.localtime(time.time())),
            get_info_from_adb()
            time.sleep(time_sleep)

# __END__

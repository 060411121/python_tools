import subprocess
import time
import getopt, sys
from pylab import *

cpu0_usage = 0
cpu1_usage = 0
cpu2_usage = 0
cpu3_usage = 0
cpu4_usage = 0
cpu5_usage = 0
cpu6_usage = 0
cpu7_usage = 0
skip = False
data_total_bak = "0 1 2 3 4 5 6 7 8"

def parse_info(data):
    global data_total_bak
    global cpu0_usage
    global cpu1_usage
    global cpu2_usage
    global cpu3_usage
    global cpu4_usage
    global cpu5_usage
    global cpu6_usage
    global cpu7_usage
    global skip

    print "len=\n"
    print data.split(" ", 10)
    a0, a1, a2, a3, a4, a5, a6, a7, other_a8 = data.split(" ", 10) 
    b0, b1, b2, b3, b4, b5, b6, b7, other_b8 = data_total_bak.split(" ", 10) 
    cpu0_usage = int(a0) - int(b0)
    cpu1_usage = int(a1) - int(b1)
    cpu2_usage = int(a2) - int(b2)
    cpu3_usage = int(a3) - int(b3)
    cpu4_usage = int(a4) - int(b4)
    cpu5_usage = int(a5) - int(b5)
    cpu6_usage = int(a6) - int(b6)
    cpu7_usage = int(a7) - int(b7)

    print data_total_bak.split(" ", 10)
    print "cpu0_usage=%d\n"%int(cpu0_usage)
    data_total_bak = data
    return;


def get_device_info_from_adb():
	command_data = "adb devices"
	proc = subprocess.Popen(command_data, shell=True, stdout=subprocess.PIPE)
	while True:
		line = proc.stdout.readline()
		if line != '':
                        if cmp(line, "List of devices attached\n") != 0:
                            if cmp(line, "\n") != 0:
			        device , other = line.split("\t", 1)
                else:
                        break
	return device;

def get_info_from_adb(cmd):
	curr_index = 0
	prev_index = 0
	info = {}
	
	command_data = "adb shell cat /acct/uid_%s/cpuacct.usage_percpu"%cmd

	proc = subprocess.Popen(command_data, shell=True, stdout=subprocess.PIPE)

	while True:
		line = proc.stdout.readline()
		if line != '':
                        parse_info(line)
                else:
                        break
	return ;

parse_all = False
show_ui = False

def usage():
	print "Usage:"
	print "\t-h               print this help"
	print "\t-a               print all list (default)"
	print "\t-t               print speed"
	print "\t-s               print total number"
	print "\t-u               show UI"
	print "\t-c               UID"
        print "\texample: xxx.py -t 2 -s 300 -c 10018 -u 10"
	return;

# __MAIN__
#com_root = "adb root"
#subprocess.call(com_root, shell=True)
#time.sleep(1)
x=[]
y=[]
y_0=[]
y_1=[]
y_2=[]
y_3=[]
y_4=[]
y_5=[]
y_6=[]
y_7=[]
if __name__ == "__main__":
        sample = 10000000
        time_sleep = 1
	try:
            opts, args = getopt.getopt(sys.argv[1:], "hals:f:vbkt:u:c:")
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
			if o == "-c":
                            cmd = a
                            parse_all = True;
			if o == "-u":
                            ui_sample = int(a)
                            show_ui = True;



if show_ui:
    print "showUI"
    fig, (ax1,ax2) = plt.subplots(1, 2, sharey=True)
    plt.ion()
if parse_all:
        device = get_device_info_from_adb()
        #print "%19s, cpu,cpu0,cpu1,cpu2,cpu3,cpu4,cpu5,cpu6,cpu7" %"time"
        for i in range(0, sample):
            print time.strftime('%Y-%m-%d %H:%M:%S,',time.localtime(time.time())),
            get_info_from_adb(cmd)
            print "%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%" %(cpu0_usage, cpu1_usage, cpu2_usage, cpu3_usage, cpu4_usage, cpu5_usage, cpu6_usage, cpu7_usage)
            if show_ui:
                x.append(i)
                y_0.append(cpu0_usage)
                y_1.append(cpu1_usage)
                y_2.append(cpu2_usage)
                y_3.append(cpu3_usage)
                y_4.append(cpu4_usage)
                y_5.append(cpu5_usage)
                y_6.append(cpu6_usage)
                y_7.append(cpu7_usage)
                if len(x) > ui_sample: 
                    x.pop(0)
                    y_0.pop(0)
                    y_1.pop(0)
                    y_2.pop(0)
                    y_3.pop(0)
                    y_4.pop(0)
                    y_5.pop(0)
                    y_6.pop(0)
                    y_7.pop(0)
                ax1.cla()
                ax2.cla()

                plt.title(device)
                ax1.plot(x, y_0, label='cpu0 %d'%cpu0_usage, lw=1)
                ax1.plot(x, y_1, label='cpu1 %d'%cpu1_usage, lw=1)
                ax1.plot(x, y_2, label='cpu2 %d'%cpu2_usage, lw=1)
                ax1.plot(x, y_3, label='cpu3 %d'%cpu3_usage, lw=1)
                ax1.set_xlabel("slave CPUs")
                ax1.legend(loc='upper left')

                ax2.plot(x, y_4, label='cpu4 %d'%cpu4_usage, lw=1)
                ax2.plot(x, y_5, label='cpu5 %d'%cpu5_usage, lw=1)
                ax2.plot(x, y_6, label='cpu6 %d'%cpu6_usage, lw=1)
                ax2.plot(x, y_7, label='cpu7 %d'%cpu7_usage, lw=1)
                ax2.set_xlabel("Gold CPUs")
                ax2.legend(loc='upper left')

                plt.pause(0.0001)
                plt.show()
            time.sleep(time_sleep)

# __END__

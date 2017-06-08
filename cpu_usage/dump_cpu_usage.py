import subprocess
import time
import getopt, sys
from pylab import *

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
cpu_usage = 0
cpu0_usage = 0
cpu1_usage = 0
cpu2_usage = 0
cpu3_usage = 0
cpu4_usage = 0
cpu5_usage = 0
cpu6_usage = 0
cpu7_usage = 0

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
    global cpu_usage
    global cpu0_usage
    global cpu1_usage
    global cpu2_usage
    global cpu3_usage
    global cpu4_usage
    global cpu5_usage
    global cpu6_usage
    global cpu7_usage
    if cmp(cpu, "cpu") == 0:
        cpu_usage = 100 - (idle-cpu_idle_bak)*100/(total-cpu_total_bak)
        cpu_idle_bak = idle
        cpu_total_bak = total
    if cmp(cpu, "cpu0") == 0:
        cpu0_usage = 100 - (idle-cpu0_idle_bak)*100/(total-cpu0_total_bak)
        cpu0_idle_bak = idle
        cpu0_total_bak = total
    if cmp(cpu, "cpu1") == 0:
        cpu1_usage = 100 - (idle-cpu1_idle_bak)*100/(total-cpu1_total_bak)
        cpu1_idle_bak = idle
        cpu1_total_bak = total
    if cmp(cpu, "cpu2") == 0:
        cpu2_usage = 100 - (idle-cpu2_idle_bak)*100/(total-cpu2_total_bak)
        cpu2_idle_bak = idle
        cpu2_total_bak = total
    if cmp(cpu, "cpu3") == 0:
        cpu3_usage = 100 - (idle-cpu3_idle_bak)*100/(total-cpu3_total_bak)
        cpu3_idle_bak = idle
        cpu3_total_bak = total
    if cmp(cpu, "cpu4") == 0:
        cpu4_usage = 100 - (idle-cpu4_idle_bak)*100/(total-cpu4_total_bak)
        cpu4_idle_bak = idle
        cpu4_total_bak = total
    if cmp(cpu, "cpu5") == 0:
        cpu5_usage = 100 - (idle-cpu5_idle_bak)*100/(total-cpu5_total_bak)
        cpu5_idle_bak = idle
        cpu5_total_bak = total
    if cmp(cpu, "cpu6") == 0:
        cpu6_usage = 100 - (idle-cpu6_idle_bak)*100/(total-cpu6_total_bak)
        cpu6_idle_bak = idle
        cpu6_total_bak = total
    if cmp(cpu, "cpu7") == 0:
        cpu7_usage = 100 - (idle-cpu7_idle_bak)*100/(total-cpu7_total_bak)
        print "%2d%%," %(cpu7_usage),
        cpu7_idle_bak = idle
        cpu7_total_bak = total

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

def get_info_from_adb():
        global cpu_usage
        global cpu0_usage
        global cpu1_usage
        global cpu2_usage
        global cpu3_usage
        global cpu4_usage
        global cpu5_usage
        global cpu6_usage
        global cpu7_usage
	curr_index = 0
	prev_index = 0
	info = {}
	
	command_data = "adb shell cat /proc/stat | grep cpu"

	proc = subprocess.Popen(command_data, shell=True, stdout=subprocess.PIPE)

        cpu_usage = 0
        cpu0_usage = 0
        cpu1_usage = 0
        cpu2_usage = 0
        cpu3_usage = 0
        cpu4_usage = 0
        cpu5_usage = 0
        cpu6_usage = 0
        cpu7_usage = 0
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
        print "\texample: xxx.py -t 2 -s 3"
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
            opts, args = getopt.getopt(sys.argv[1:], "hals:f:vbkt:u:")
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
			if o == "-u":
                            ui_sample = int(a)
                            show_ui = True;



if show_ui:
    print "showUI"
    fig, (ax,ax0,ax1,ax2,ax3,ax4,ax5,ax6,ax7) = plt.subplots(9, 1, sharey=True)
    plt.ion()
if parse_all:
	# Dump PM8998 LDO info.
        device = get_device_info_from_adb()
        print "hshdhah%s" %device
        print "%19s, cpu,cpu0,cpu1,cpu2,cpu3,cpu4,cpu5,cpu6,cpu7" %"time"
        for i in range(0, sample):
            print time.strftime('%Y-%m-%d %H:%M:%S,',time.localtime(time.time())),
            get_info_from_adb()
            print "%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%,%2d%%" %(cpu_usage, cpu0_usage, cpu1_usage, cpu2_usage, cpu3_usage, cpu4_usage, cpu5_usage, cpu6_usage, cpu7_usage)
            if show_ui:
                x.append(i)
                y.append(cpu_usage)
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
                    y.pop(0)
                    y_0.pop(0)
                    y_1.pop(0)
                    y_2.pop(0)
                    y_3.pop(0)
                    y_4.pop(0)
                    y_5.pop(0)
                    y_6.pop(0)
                    y_7.pop(0)
                ax.cla()
                ax0.cla()
                ax1.cla()
                ax2.cla()
                ax3.cla()
                ax4.cla()
                ax5.cla()
                ax6.cla()
                ax7.cla()
                ax.set_title(device)
                ax.plot(x, y, 'b')
                ax0.plot(x, y_0, 'b')
                ax1.plot(x, y_1, 'b')
                ax2.plot(x, y_2, 'b')
                ax3.plot(x, y_3, 'b')
                ax4.plot(x, y_4, 'b')
                ax5.plot(x, y_5, 'b')
                ax6.plot(x, y_6, 'b')
                ax7.plot(x, y_7, 'b')
                plt.pause(0.0001)
                plt.show()
            time.sleep(time_sleep)

# __END__

import subprocess as s
import re
#if(ch==1):
print("Hadoop Setup")	

IP=list()
pingname=list()


print("Name Node details-")
IP.append(input("Enter IP: "))
pingname.append(input("Enter the ping name: "))

print("Client Node details")
IP.append(input("Enter IP: "))
pingname.append(input("Enter the ping name: "))     


print("Data Nodes details-")
num_dn=input("Enter the number of data nodes in the cluster you prefer to have:")
num_dn=int(num_dn)

for i in range(num_dn):
	print("Enter the IP and the ping name of data node {}-".format((i+1)))
	IP.append(input('Enter IP: '))
	pingname.append(input('Enter ping name: '))
	print(IP[i+2])
	print(pingname[i+2])
print("Basic draft ready")

len_IP=len(IP)


print("------------------")
print("SERVER")
print("------------------")
print("Let's set up Hadoop")
print("step-1 : Let's check network connectivity")

flag_net=True


for i in range(len_IP):
	
	output =s.getoutput("ping {} -c1".format(IP[i]))
	

	if (re.search('ttl',output)):
		print("{} OK".format(pingname[i]))
	else:
		print("Network problem with {}".format(pingname[i]))
		flag_net=False


if(flag_net==False):
	print("	Please rectify the above errors befor continuing ")
	s.getoutput('exit')
else:
	print("Congrats Step-1 working fine\n ")





print("Step-2: Update host address book with the given inputs")
s.getoutput('cp /etc/hosts /tmp/hosts.xml')
addr_loc_hosts=open('/tmp/hosts.xml','r+')
for i in range(len_IP):
	addr_loc_hosts.write('{}\t{}\n'.format(IP[i],pingname[i]))
addr_loc_hosts.close()
for i in range(len_IP):
	s.getoutput("scp /tmp/hosts.xml {}:/etc/hosts".format(IP[i]))

print('Congrats 2nd step done, hosts file updated')

print('Step-3 Now check if all the pings are working or not')
flag_pingname=True

for i in range(len_IP):

	output =s.getoutput('ping {} -c1'.format(pingname[i]))
	if(re.search('ttl',output)):
		print('{} OK'.format(pingname[i]))
	else:
		print('{} pingname error'.format(pingname[i]))
		flag_pingname=False

if(flag_pingname==False):
	print("Please check your /etc/hosts file again.")
else:
	print('Congrats 3rd step done. All hostname are properly assigned')

print('Step 4: Turn off fire wall permanently')
s.getoutput("cp /etc/rc.d/rc.local /tmp/rc.local")
x=open('/tmp/rc.local','r+')
x.read() # this will bring us to the end of file, since we want to write in the file's end
x.write("\n iptables -F \n")
x.close()


for i in range(len_IP):
	s.getoutput("scp /tmp/rc.local {}:/etc/rc.d/rc.local".format(IP[i]))

print("Firewall permanently closed")


print("Let us install the java Hadoop into the system")
print("JAVA -")

print("let us check if java is already installed or not")

for i in range(len_IP):

	output=s.getoutput("ssh {} java -version".format(IP[i]))	
	if(re.search('HotSpot',output)):
		print("already installed")
	else:
		print("not present")
		path=input('Please Enter where jdk folder is located: ')
		s.getoutput("ssh {} rpm -ivh --force {}/jdk-8u171-linux-x64.rpm".format(IP[i],path))
		print('Java installation done')
		#we are executing the step once becuase in bash.rc file the new effect comes only when u open a new file
s.getoutput("cp /root/.bashrc /tmp/.bashrc")
x=open('/tmp/.bashrc','r+')
x.read()
x.write("\n JAVA_PATH=/usr/java/jdk-8u171-linux-x64.rpm \n PATH=$JAVA_PATH/bin:$PATH\n")
x.close()

for i in range(len_IP):
	s.getoutput("scp /tmp/.bashrc {}:/root/.bashrc".format(IP[i]))


print("let us check the hadoop installation")

for i in range(len_IP):
	
	output=s.getoutput("ssh {} hadoop version".format(IP[i]))

	if(re.search('Hadoop 1.2.1',output)):
		print("already installed")
	else:
		print("not present")
		path=input('Please Enter where Hadoop folder is located: ')
		s.getoutput("ssh {} rpm -ivh --force {}/hadoop-1.2.1-1.x86_64.rpm".format(IP[i],path))
		print('Hadoop installation done')


print("java , hadoop done")

print("With all pre-requisites done, let us setup Hadoop cluster")


print()
print("---------------HADOOP-------------------")
print()


print("NAME NODE")
#/name folder setup

s.getoutput("ssh {} mkdir /name".format(IP[0]))
s.getoutput("cp /etc/hadoop/hdfs-site.xml /tmp/nn_hdfs-site.xml")
x=open("/tmp/nn_hdfs-site.xml","w")
str="""<?xml version='1.0'?>
<?xml-stylesheet type='text/xsl' href='configuration.xsl'?>

<!-- Put site-specific property overrides in this file. -->

<configuration>
<property>
<name>dfs.name.dir</name>
<value>/name</value>
</property>
</configuration>"""
x.write(str)
x.close()

s.getoutput("scp /tmp/nn_hdfs-site.xml {}:/etc/hadoop/hdfs-site.xml".format(IP[0]))

s.getoutput("cp /etc/hadoop/core-site.xml /tmp/core-site.xml")

x=open("/tmp/core-site.xml","w")
nnport=input("Enter the port number of nn: ")
str="""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<!-- Put site-specific property overrides in this file. -->

<configuration>
<property>
<name>fs.default.name</name>
<value>hdfs://{}:{}</value>
</property>
</configuration>""".format(IP[0],nnport)
x.write(str)
x.close()

for i in range(len_IP):
	s.getoutput("scp /tmp/core-site.xml {}:/etc/hadoop/core-site.xml".format(IP[i]))
	

s.getoutput("cp /etc/hadoop/hdfs-site.xml /tmp/dn_hdfs-site.xml")
x=open("/tmp/dn_hdfs-site.xml","w")
str="""<?xml version='1.0'?>
<?xml-stylesheet type='text/xsl' href='configuration.xsl'?>

<!-- Put site-specific property overrides in this file. -->

<configuration>
<property>
<name>dfs.data.dir</name>
<value>/data</value>
</property>
</configuration>"""
x.write(str)
x.close()

for i in range(2,len_IP):
	s.getoutput("ssh {} mkdir /data".format(IP[i]))
	s.getoutput("scp /tmp/dn_hdfs-site.xml {}:/etc/hadoop/hdfs-site.xml".format(IP[i]))


#all data nodes done
print("Success updation of files")



flagss=True

print("-----------NAME NODE----------")
a=s.getoutput("ssh {} mkdir /name".format(IP[0]))

if(re.search("exists",a)):
	print("False")
	flagss=False
else:
	print("True")
	flagss=True
if(flagss==False):
	a=s.getoutput("echo Y | ssh {} hadoop namenode -format ".format(IP[0]))
	print(a)
a=s.getoutput("ssh {} hadoop-daemon.sh start namenode".format(IP[0]))
print(a)

if(re.search('NameNode',output)==None):
	print("Check if your firewall is off or check your spelling mistake")

for i in range(2,len_IP):
	print("-----------DATANODE-----------")

	if(flagss==False):
		output=s	.getoutput("ssh {} mkdir /data".format(IP[i]))
		print(output)
	output=s.getoutput("ssh {} hadoop-daemon.sh start datanode".format(IP[i]))
	print(output)
	
	output=s.getoutput("ssh {} jps".format(IP[i]))
	if(re.search('DataNode',output)==None):
		print("Check if your firewall is off or check your spelling mistake")

print("With all the processing doen let us check if our hadoop cluster is working or not")
output = s.getoutput("ssh {} hadoop dfsadmin -report".format(IP[0]))
print(output)

print("-----------CLIENT NODE----------")
s.getoutput("ssh {} hadoop-daemon.sh start clientnode".format(IP[1]))
print("aaaaaaaaaaaaaaaaaaaaaaaa")
s.getoutput("ssh {} hadoop-daemon.sh enable clientnode".format(IP[1]))
output=s.getoutput("ssh {} jps".format(IP[1]))
if(re.search('hadoop',output)==None):
	print("Check if your firewall is off or check your spelling mistake")

print("Hadoop cluster made")




print("So far we have made hadoop distributed file system")
print("\t\t\t ------------ HDFS done ------------------")
print()
print()
print("------------------MR -----------------")
print()
print("HDFS Cluster")
print()
print("so far we have made hdfs and client , client will be common for both MR and HDFS , now let us make computing or MR cluster")
IP_MR=[]
pingname_MR=[]

print("Enter the IP and pingname of the systems you want to make cluster with-")
print("***Job Tracker aka master node***")
IP_MR.append(input("Enter the IP:"))
pingname_MR.append(input("Enter the ping name:"))
print("***Job Tracker aka slave nodes***")
num_tt=input("Enter the number of job trackers you want for your cluster:")
num_tt=int(num_tt) #since we get string from input , so we need to convert it into int
for i in range(num_tt):
	print("Enter the IP and ping name for tt[{}]".format((i+1)))
	IP_MR.append(input("Enter the IP:"))
	pingname_MR.append(input("Enter the ping name:"))


len_IP_MR=len(IP_MR)
flag_net=True

for i in range(len_IP_MR):
	#since for me to make change I ned to be in same network , so if I am able to ping implies everyone can ping each other
	output =s.getoutput("ping {} -c1".format(IP_MR[i]))
	if (re.search('ttl',output)):
		print("{} OK".format(pingname_MR[i]))
	else:
		print("Network problem with {}".format(pingname_MR[i]))
		flag_net=False


if(flag_net==False):
	print("	Please rectify the above errors befor continuing ")
	s.getoutput('exit')
else:
	print("Congrats Step-1 working fine\n ")





print("Step-2: Update host address book with the given inputs")
#client-
s.getoutput("scp {}:/etc/hosts /tmp/hosts.xml ".format(IP[1]))
addr_loc_hosts=open('/tmp/hosts.xml','r+')
for i in range(len_IP_MR):
	addr_loc_hosts.write('{}\t{}\n'.format(IP_MR[i],pingname_MR[i]))
addr_loc_hosts.close()
s.getoutput("scp /tmp/hosts.xml {}:/etc/hosts".format(IP[1]))



s.getoutput('cp /etc/hosts /tmp/hosts.xml')
addr_loc_hosts=open('/tmp/hosts.xml','r+')
for i in range(len_IP_MR):
	addr_loc_hosts.write('{}\t{}\n'.format(IP_MR[i],pingname_MR[i]))
addr_loc_hosts.close()
for i in range(len_IP_MR):
	s.getoutput("scp /tmp/hosts.xml {}:/etc/hosts".format(IP_MR[i]))

print('Congrats 2nd step done, hosts file updated')

print('Step-3 Now check if all the pings are working or not')
flag_pingname=True

for i in range(len_IP_MR):

	output =s.getoutput('ping {} -c1'.format(pingname_MR[i]))
	if(re.search('ttl',output)):
		print('{} OK'.format(pingname_MR[i]))
	else:
		print('{} pingname error'.format(pingname_MR[i]))
		flag_pingname=False

if(flag_pingname==False):
	print("Please check your /etc/hosts file again.")
else:
	print('Congrats 3rd step done. All hostname are properly assigned')

print('Step 4: Turn off fire wall permanently')
#rc.local already updated
for i in range(len_IP_MR):
	s.getoutput("scp /tmp/rc.local {}:/etc/rc.d/rc.local".format(IP_MR[i]))

print("Firewall permanently closed")


print("Let us install the java Hadoop into the system")
print("JAVA -")

print("let us check if java is already installed or not")

for i in range(len_IP_MR):

	output=s.getoutput("ssh {} java -version".format(IP_MR[i]))	
	if(re.search('HotSpot',output)):
		print("already installed")
	else:
		print("not present")
		path=input('Please Enter where jdk folder is located: ')
		s.getoutput("ssh {} rpm -ivh --force {}/jdk-8u171-linux-x64.rpm".format(IP_MR[i],path))
		print('Java installation done')
		#we are executing the step once becuase in bash.rc file the new effect comes only when u open a ,ALREADY MADE

for i in range(len_IP_MR):
	s.getoutput("scp /tmp/.bashrc {}:/root/.bashrc".format(IP_MR[i]))


print("let us check the hadoop installation")

for i in range(len_IP_MR):
	
	output=s.getoutput("ssh {} hadoop version".format(IP_MR[i]))

	if(re.search('Hadoop 1.2.1',output)):
		print("already installed")
	else:
		print("not present")
		path=input('Please Enter where Hadoop folder is located: ')
		s.getoutput("ssh {} rpm -ivh --force {}/hadoop-1.2.1-1.x86_64.rpm".format(IP_MR[i],path))
		print('Hadoop installation done')


print("java , hadoop done")

print("With all pre-requisites done, let us setup Hadoop MR cluster")

print("JOB TRACKER")



print("Now scp the mapred site file to other nodes")
s.getoutput("cp /etc/hadoop/mapred-site.xml /tmp/mapred-site.xml")
port=input("Enter the port number: ")
x=open("/tmp/mapred-site.xml","w")
str="""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<!-- Put site-specific property overrides in this file. -->

<configuration>
<property>
<name>mapred.job.tracker</name>
<value>{}:{}</value>
</property>
</configuration>""".format(pingname_MR[0],port)
x.write(str)
x.close()

for i in range(len_IP_MR):
	s.getoutput("scp /tmp/mapred-site.xml {}:/etc/hadoop/mapred-site.xml".format(IP_MR[i]))
#client
s.getoutput("scp /tmp/mapred-site.xml {}:/etc/hadoop/mapred-site.xml".format(IP[1]))	
#all Task Trackers done
print("Success updation of files")

print("-----------JOB TRACKER----------")
output=s.getoutput("ssh {} hadoop-daemon.sh start jobtracker".format(IP_MR[0]))
print(output)
output=s.getoutput("ssh {} jps".format(IP_MR[0]))
print(output)
if(re.search('JobTracker',output)==None):
	print("Check if your firewall is off or check your spelling mistake")

for i in range(len_IP-1):
	print("-----------DATANODE-----------")
	output=s.getoutput("ssh {} hadoop-daemon.sh start tasktracker".format(IP_MR[i]))
	print(output)
	output=s.getoutput("ssh {} jps".format(IP_MR[i]))
	print(output)
	if(re.search('TaskTracker',output)==None):
		print("Check if your firewall is off or check your spelling mistake")

print("With all the processing doen let us check if our hadoop cluster is working or not")
output = s.getoutput("ssh {} hadoop job -list-active-trackers".format(IP_MR[0]))
print(output)


print("-----------------DONEEE-------------")







































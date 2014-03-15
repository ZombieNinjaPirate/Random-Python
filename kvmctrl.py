#!/usr/bin/env python


"""
Remote KVM management script.

Connects to a KVM server using SSH and executes commands that controls the KVM guest
machines. SSH keys must be present on the server and the virsh command must be allowed to
run as the user using sudo, but without having to type a password.
"""


__date__ = '2013, November 8'
__author__ = 'Black September'
__version__ = '1.0.8'


import argparse
import paramiko
import sys
import socket


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Remote management of KVM machines.')

    host = parser.add_argument_group('KVM host specific arguments')
    host.add_argument('-H', '--host', help='Hostname', required=True)
    host.add_argument('-U', '--user', help='Username', required=True)
    host.add_argument('-L', '--list', help='Lists all defined KVMs', action='store_true')

    kvm = parser.add_argument_group('KVM control arguments')
    kvm.add_argument('-B', '--start', help='Start [kvm]')
    kvm.add_argument('-S', '--shutdown', help='Shutdown [kvm]')
    kvm.add_argument('-R', '--reboot', help='Reboot [kvm]')
    kvm.add_argument('-I', '--info', help='Information about [kvm]')

    resources = parser.add_argument_group('Resource control arguments')
    resources.add_argument('-K', '--kvm', help='KVM name')
    resources.add_argument('-r', '--ram', help='Amount of RAM in MiB', type=int)
    resources.add_argument('-c', '--cpu', help='Number of CPU cores', type=int)

    args = parser.parse_args()

    return args


def list_kvms(virsh):
    """
    Lists all the defined and running kvm's.
    """
    cmd = '{0} list --all;'.format(virsh)
    list_all_kvms = [cmd]

    return list_all_kvms


def start_kvm(virsh, kvm, state):
    """
    Starts a kvm, if state is shutdown. Exit with 1 if running.
    """
    if state is 'SHUTDOWN':
        cmd = '{0} start {1}'.format(virsh, kvm)
        start = [cmd]
        print 'Atempting to start {0} now...'.format(kvm)
    elif state is 'RUNNING':
        print 'ERROR: Cant start {0}. State is: {1}'.format(kvm, state)
        sys.exit(1)

    return start


def shutdown_kvm(virsh, kvm, state):
    """
    Shutsdown a kvm, if state is running. Exit with 1 if not running.
    """
    if state is 'RUNNING':
        cmd = '{0} shutdown {1}'.format(virsh, kvm)
        shutdown = [cmd]
        print 'Atempting to shutdown {0} now...'.format(kvm)
    elif state is 'SHUTDOWN':
        print 'ERROR: Cant shutdown {0}. State is: {1}'.format(kvm, state)
        sys.exit(1)

    return shutdown


def reboot_kvm(virsh, kvm, state):
    """
    Reboots a kvm, if its running. Exit with 1 if not running.
    """
    if state is 'RUNNING':
        cmd = '{0} reboot {1}'.format(virsh, kvm)
        reboot = [cmd]
        print 'Atempting to reboot {0} now...'.format(kvm)
    elif state is 'SHUTDOWN':
        print 'ERROR: Cant reboot {0}. State is: {1}.'.format(kvm, state)
        sys.exit(1)

    return reboot


def info_kvm(virsh, kvm):
    """
    Request information about the kvm.
    """
    cmd = '{0} dominfo {1}'.format(virsh, kvm)
    info_about_kvm = [cmd]
    print 'Fetching information about {0}...'.format(kvm)

    return info_about_kvm


def change_cpu(kvm, virsh, new_cpu, state):
    """
    Changes the number of assigned CPU cores the kvm has access to. If the kvm is running
    it will first be shutdown, assigned the new CPU values and then started again. It the
    kvm is not running, the new CPU values will be assigned to it but not booted.
    """
    wait = 'sleep 2'
    max_cpu = new_cpu

    if state is 'RUNNING':
        stop = '{0} shutdown {1} &>/dev/null'.format(virsh, kvm)
        set_maxcpu = '{0} setvcpus {1} --maximum {2} --config'.format(virsh, kvm, max_cpu)
        set_newcpu = '{0} setvcpus {1} {2} --config'.format(virsh, kvm, new_cpu)
        start = '{0} start {1}'.format(virsh, kvm)
        change_cpu_cmd = [stop, wait, set_maxcpu, set_newcpu, wait, start]
        print "Number of CPU's after reboot {0}. State {1}".format(new_cpu, state)
    elif state is 'SHUTDOWN':
        set_maxcpu = '{0} setvcpus {1} --maximum {2} --config'.format(virsh, kvm, max_cpu)
        set_newcpu = '{0} setvcpus {1} {2} --config'.format(virsh, kvm, new_cpu)
        change_cpu_cmd = [set_maxcpu, set_newcpu]
        print "State of {0} is {1}, {2} CPU's at next boot.".format(kvm, state, new_cpu)

    return change_cpu_cmd


def change_ram(kvm, virsh, new_ram, state):
    """
    Changes the assigned amount of RAM the kvm has access to. If the kvm is running it
    will first be shutdown, assigned the new RAM values and then started again. It the kvm
    is not running, the new RAM values will be assigned to it but not booted. The assigned
    RAM values are converted from MiB to KiB's. The maximum amount of RAM has to be bigger
    than the actual amoount of assigned RAM.
    The amount of assigned RAM is calculated as: assigned RAM * 1024
    The max amount of RAM is calculated as: assigned RAM * 1025
    """
    wait = 'sleep 2'
    max_ram = int(new_ram) * 1025
    new_ram = int(new_ram) * 1024

    if state is 'RUNNING':
        kvm_stop = '{0} shutdown {1}'.format(virsh, kvm)
        set_maxmem = '{0} setmaxmem {1} {2} --config'.format(virsh, kvm, max_ram)
        set_mem = '{0} setmem {1} {2} --config'.format(virsh, kvm, new_ram)
        kvm_start = '{0} start {1}'.format(virsh, kvm)
        add_ram_cmds = [kvm_stop, wait, set_maxmem, set_mem, wait, kvm_start]
        print 'Amount of RAM after reboot: {0} KiB. Rebooting now...'.format(new_ram)
    elif state is 'SHUTDOWN':
        set_maxmem = '{0} setmaxmem {1} {2} --config'.format(virsh, kvm, max_ram)
        set_mem = '{0} setmem {1} {2} --config'.format(virsh, kvm, new_ram)
        add_ram_cmds = [set_maxmem, set_mem]
        print 'Amount of for {0} RAM at next boot: {1} KiB.'.format(kvm, new_ram)

    return add_ram_cmds


def ssh_rexec(rhost, ruser, cmd_list):
    """
    Itterates trough the list of commands, connects to the remote host and executes the
    commands one by one. Returns stdout if the commnands exit with '0', else it returns
    stderr.
    """
    for i in range(len(cmd_list)):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(rhost, username=ruser)

        except paramiko.AuthenticationException:
            print 'ERROR: Authentication as {0}@{1} failed.'.format(ruser, rhost)
            ssh.close()
            sys.exit(1)

        except socket.error:
            print 'ERROR: Connection to {0} failed.'.format(rhost)
            ssh.close()
            sys.exit(1)

        stdin, stdout, stderr = ssh.exec_command(cmd_list[i])
        exit_status = stdout.channel.recv_exit_status()
        ssh.close()

    if str(exit_status) == '0':
        return stdout.readlines()
    else:
        return stderr.readlines()


def read_output(textlines):
    """
    Reads the returned output and prints it to stdout.
    """
    for lines in textlines:
        print lines,


def kvm_state(kvmlist, kvm):
    """
    Strips the kvmlist down to only containing names and builds a dictionary from that.
    The dictionary is searched for a key matching kvm and will pass if found,exit 1 and
    prints error message if not. Then it checks the running state of the kvm.
    """
    kvm_dict = {}
    del kvmlist[0:2]
    del kvmlist[-1]

    for k in kvmlist:
        k_list = k.split()
        del k_list[0]
        del k_list[1:]

        for name in k_list:
            kvm_dict[name] = name

    if kvm in kvm_dict.keys():
        pass
    else:
        print 'ERROR: {0} dont exist!'.format(kvm)
        sys.exit(1)

    for k in kvmlist:
        if kvm in k:
            if 'running' in k:
                state = 'RUNNING'
            elif 'shut off' in k:
                state = 'SHUTDOWN'

    return state


def process_check(args):
    """
    Preform basic checking of the arguments.
    """
    rhost = args.host
    ruser = args.user
    listall = args.list
    kvm = args.kvm
    start = args.start
    shutdown = args.shutdown
    reboot = args.reboot
    info = args.info
    new_ram = args.ram
    new_cpu = args.cpu
    virsh = 'sudo /usr/bin/virsh -c qemu:///system'

    if listall:
        read_output(ssh_rexec(rhost, ruser, list_kvms(virsh)))

    if start:
        curr_state = kvm_state(ssh_rexec(rhost, ruser, list_kvms(virsh)), start)
        read_output(ssh_rexec(rhost, ruser, start_kvm(virsh, start, curr_state)))

    if shutdown:
        curr_state = kvm_state(ssh_rexec(rhost, ruser, list_kvms(virsh)), shutdown)
        read_output(ssh_rexec(rhost, ruser, shutdown_kvm(virsh, shutdown, curr_state)))

    if reboot:
        curr_state = kvm_state(ssh_rexec(rhost, ruser, list_kvms(virsh)), reboot)
        read_output(ssh_rexec(rhost, ruser, reboot_kvm(virsh, reboot, curr_state)))

    if info:
        read_output(ssh_rexec(rhost, ruser, info_kvm(virsh, info)))

    if new_ram and kvm:
        curr_state = kvm_state(ssh_rexec(rhost, ruser, list_kvms(virsh)), kvm)
        read_output(ssh_rexec(rhost, ruser, change_ram(kvm, virsh, new_ram, curr_state)))
    elif new_ram and not kvm:
        print 'ERROR: -K/--kvm is required when changing the amount of RAM.'
        sys.exit(1)

    if kvm and new_cpu:
        curr_state = kvm_state(ssh_rexec(rhost, ruser, list_kvms(virsh)), kvm)
        read_output(ssh_rexec(rhost, ruser, change_cpu(kvm, virsh, new_cpu, curr_state)))
    elif new_cpu and not kvm:
        print 'ERROR: -K/--kvm is required when changing the amount of RAM.'
        sys.exit(1)

    if kvm and len(sys.argv) <= 7:
        print 'ERROR: Giving me the name of a KVM wont do much...Try -h/--help!'
        sys.exit(1)

    if ruser and rhost and len(sys.argv) == 5:
        print 'ERROR: You should try reading the manual-h/--help!'
        sys.exit(1)


def main():
    """
    Ze Bozz function.
    """
    args = parse_args()
    process_check(args)


if __name__ == '__main__':
    main()
  

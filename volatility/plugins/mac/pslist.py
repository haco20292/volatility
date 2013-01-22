# Volatility
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 

"""
@author:       Andrew Case
@license:      GNU General Public License 2.0 or later
@contact:      atcuno@gmail.com
@organization: 
"""
import time

import volatility.obj as obj
import common

class mac_pslist(common.AbstractMacCommand):
    """ List Running Processes """

    def __init__(self, config, *args):
        common.AbstractMacCommand.__init__(self, config, *args)
        self._config.add_option('PID', short_option = 'p', default = None, help = 'Operate on these Process IDs (comma-separated)', action = 'store', type = 'str')

    def calculate(self):
        common.set_plugin_members(self)

        pidlist = None

        try:
            if self._config.PID:
                pidlist = [int(p) for p in self._config.PID.split(',')]
        except:
            pass
        
        p = self.get_profile_symbol("_allproc")

        procsaddr = obj.Object("proclist", offset=p, vm=self.addr_space)

        proc = obj.Object("proc", offset=procsaddr.lh_first, vm=self.addr_space)

        while proc.p_list.le_next:
    
            if not pidlist or proc.p_pid in pidlist:
                yield proc 

            proc = proc.p_list.le_next

    #### move this to an overlay for 'proc'
    def _get_proc_start_time(self, proc):
        nsecs_per = 1000000
        
        start_time = proc.p_start 

        start_secs = start_time.tv_sec + (start_time.tv_usec / nsecs_per)

        sec = start_secs

        # protect against invalid data in unallocated tasks
        try:
            ret = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(sec))
        except ValueError:
            ret = ""

        return ret

    def render_text(self, outfd, data):
        self.table_header(outfd, [("Offset", "[addrpad]"),
                          ("Name", "20"),
                          ("Pid", "15"),
                          ("Uid", "15"),
                          ("Gid", "9"),
                          ("Start Time", "")])

        for proc in data:
            name = common.get_string(proc.p_comm.obj_offset, self.addr_space)
            self.table_row(outfd, proc.obj_offset,
                                  name,
                                  str(proc.p_pid),
                                  str(proc.p_ucred.cr_uid),
                                  str(proc.p_ucred.cr_gmuid),
                                  self._get_proc_start_time(proc))







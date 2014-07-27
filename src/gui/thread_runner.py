#    Brachyprint -- 3D printing brachytherapy moulds
#    Copyright (C) 2013-14  James Cranch, Martin Green and Oliver Madge
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import wx
import wx.lib.newevent

from threading import Thread, current_thread

import time


class ThreadRunner(wx.EvtHandler):
    '''
    A thread runner.

    Example usage:
        
            def loop_callback(ret):
                self.thread_button.SetLabel("Count = %i" % ret[0])

            def done_callback():
                self.thread_button.SetLabel("Done")

            def work():
                for i in range(10):
                    time.sleep(1)
                    yield i

            self.thread_button = wx.Button(self, label="Launch thread")

            self.thread = ThreadRunner(work, done_callback, loop_callback)

            self.thread_button.Bind(wx.EVT_BUTTON, lambda x: self.thread.start())

    '''

    def OnThreadedResultEvent(self, event):
        '''Receive events from threads.
        '''
        if not hasattr(event, 'args'):
            event.args = {}
        if not hasattr(event, 'kwargs'):
            event.kwargs = {}
        event.func(*event.args, **event.kwargs)


    def __init__(self, generator, callback, loop_callback=None):
        (self.ThreadedResultEvent, EVT_THREAD_RESULT) = wx.lib.newevent.NewEvent()

        self.evt_handler = wx.EvtHandler()
        self.evt_handler.Bind(EVT_THREAD_RESULT, self.OnThreadedResultEvent)

        self.generator = generator
        self.callback = callback
        self.loop_callback = loop_callback

    def _start(self, *args, **kwargs):
        self._stopped = False
        for ret in self.generator(*args, **kwargs):
            if self._stopped:
                break
                #thread.exit()
            if self.loop_callback is not None:
                self._loop(ret)
        # XXX: hack to stop wxProgressDialog from misordering Update() and Destroy(). Sigh.
        time.sleep(0.1)
        if self.callback is not None:
            wx.PostEvent(self.evt_handler, self.ThreadedResultEvent(func=self.callback))

    def _loop(self, ret):
        if ret is None:
            ret = ()
        if not isinstance(ret, tuple):
            ret = (ret,)
        wx.PostEvent(self.evt_handler, self.ThreadedResultEvent(func=self.loop_callback, kwargs={'ret': ret}))

    def start(self, *args, **kwargs):
        # TODO: consider putting a lock here to stop multiple thread invocations
        Thread(target=self._start, args=args, kwargs=kwargs).start()

    def stop(self):
        self._stopped = True


class ThreadProgressDialog(ThreadRunner):
    '''
    Example usage:

    wx.Window()...
        self.thread = ThreadProgressDialog(self, work)
        self.thread.start()
    '''

    def __init__(self, parent, generator):
        super(ThreadProgressDialog, self).__init__(generator, self.destroy_dialog, self.display_progress)

        self.dlg = None
        self.parent = parent


    def display_progress(self, ret):
        if self.dlg:
            (tocontinue, skip) = self.dlg.Update(ret[0])
            if not tocontinue:
                self.stop()

    def destroy_dialog(self):
        self.dlg.Destroy()
        self.dlg = None

    def start(self, *args, **kwargs):
        self.dlg = wx.ProgressDialog("Please wait...",
                               "",
                               maximum = 10,
                               parent=self.parent,
                               style = 0
                                | wx.PD_APP_MODAL
                                | wx.PD_CAN_ABORT
                                #| wx.PD_CAN_SKIP
                                #| wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                #| wx.PD_AUTO_HIDE
                                )

        super(ThreadProgressDialog, self).start(*args, **kwargs)


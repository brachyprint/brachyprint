
import wx
import wx.lib.newevent

from threading import Thread

class ThreadDispatcher(wx.EvtHandler):
    '''
    A thread dispatcher.

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

            self.thread_button.Bind(wx.EVT_BUTTON, lambda x: self.thread.start(work, done_callback, loop_callback))

            self.thread = ThreadDispatcher()
    '''

    def OnThreadedResultEvent(self, event):
        '''Receive events from threads.
        '''
        if not hasattr(event, 'args'):
            event.args = {}
        if not hasattr(event, 'kwargs'):
            event.kwargs = {}
        event.func(*event.args, **event.kwargs)


    def __init__(self):
        (self.ThreadedResultEvent, EVT_THREAD_RESULT) = wx.lib.newevent.NewEvent()

        self.evt_handler = wx.EvtHandler()
        self.evt_handler.Bind(EVT_THREAD_RESULT, self.OnThreadedResultEvent)

    def _start(self, generator, callback, loop_callback, *args, **kwargs):
        self._stopped = False
        for ret in generator(*args, **kwargs):
            if self._stopped:
                thread.exit()
            if loop_callback is not None:
                self._loop(loop_callback, ret)
        if callback is not None:
            wx.PostEvent(self.evt_handler, self.ThreadedResultEvent(func=callback, args=args, kwargs=kwargs))

    def _loop(self, loop_callback, ret):
        if ret is None:
            ret = ()
        if not isinstance(ret, tuple):
            ret = (ret,)
        wx.PostEvent(self.evt_handler, self.ThreadedResultEvent(func=loop_callback, kwargs={'ret': ret}))

    def start(self, generator, callback, loop_callback=None, *args, **kwargs):
        if args:
            Thread(target=self._start, args=[generator, callback, loop_callback, args], kwargs=kwargs).start()
        else:
            Thread(target=self._start, args=[generator, callback, loop_callback]).start()

    def stop(self):
        self._stopped = True


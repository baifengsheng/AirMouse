import platform
import threading
import time


_CANDIDATE_AUTOMATION_IDS = {
    "IME_Candidate_Window",
    "IME_Prediction_Window",
}
_CANDIDATE_TEXT_AUTOMATION_ID = "TEMPLATE_PART_CandidateItemText"


class ImeCandidateMonitor:
    def __init__(self):
        self._emit = None
        self._thread = None
        self._refresh_requested = threading.Event()
        self._state_lock = threading.Lock()
        self._candidate_control = None
        self._last_candidates = ()
        self._supported = platform.system() == "Windows"

    @property
    def supported(self):
        return self._supported

    def start(self, emit_callback):
        self._emit = emit_callback
        if not self._supported or (self._thread and self._thread.is_alive()):
            return self._supported

        self._thread = threading.Thread(
            target=self._run,
            name="ime-candidate-monitor",
            daemon=True,
        )
        self._thread.start()
        return True

    def request_refresh(self):
        if self._supported:
            self._refresh_requested.set()

    def snapshot(self):
        with self._state_lock:
            return {
                "candidates": list(self._last_candidates),
                "supported": self._supported,
            }

    def _publish(self, candidates):
        normalized = tuple(candidates[:9])
        with self._state_lock:
            if normalized == self._last_candidates:
                return
            self._last_candidates = normalized

        if self._emit:
            self._emit({
                "candidates": list(normalized),
                "supported": self._supported,
            })

    def _extract_candidates(self, candidate_control, auto):
        candidates = []

        for control, _depth in auto.WalkControl(
            candidate_control,
            includeTop=False,
            maxDepth=4,
        ):
            if control.AutomationId != _CANDIDATE_TEXT_AUTOMATION_ID:
                continue
            text = (control.Name or "").strip()
            if text and text not in candidates:
                candidates.append(text)
            if len(candidates) >= 9:
                break

        if candidates:
            return candidates

        for control, _depth in auto.WalkControl(
            candidate_control,
            includeTop=False,
            maxDepth=3,
        ):
            if control.ControlTypeName != "ListItemControl":
                continue
            text = (control.Name or "").strip()
            if text and text not in candidates:
                candidates.append(text)
            if len(candidates) >= 9:
                break

        return candidates

    def _find_candidate_control(self, auto):
        with self._state_lock:
            cached = self._candidate_control

        if cached is not None:
            try:
                if cached.AutomationId in _CANDIDATE_AUTOMATION_IDS:
                    return cached
            except Exception:
                pass

        root = auto.GetRootControl()
        for automation_id in _CANDIDATE_AUTOMATION_IDS:
            control = auto.Control(
                searchFromControl=root,
                AutomationId=automation_id,
                searchDepth=8,
                searchInterval=0.01,
            )
            if control.Exists(0.08, 0.01):
                with self._state_lock:
                    self._candidate_control = control
                return control

        return None

    def _refresh(self, auto):
        for attempt in range(3):
            candidate_control = self._find_candidate_control(auto)
            if candidate_control is not None:
                try:
                    candidates = self._extract_candidates(candidate_control, auto)
                    if candidates:
                        self._publish(candidates)
                        return
                except Exception:
                    with self._state_lock:
                        self._candidate_control = None

            if attempt < 2:
                time.sleep(0.035)

        self._publish([])

    def _run(self):
        try:
            import comtypes.client
            from comtypes import COMObject
            import uiautomation as auto
            import uiautomation.uiautomation as auto_impl

            with auto.UIAutomationInitializerInThread():
                client = auto_impl._AutomationClient.instance()
                core = client.UIAutomationCore
                automation = client.IUIAutomation
                monitor = self

                class AutomationEventHandler(COMObject):
                    _com_interfaces_ = [core.IUIAutomationEventHandler]

                    def HandleAutomationEvent(self, sender, event_id):
                        try:
                            control = auto.Control.CreateControlFromElement(sender)
                            if control.AutomationId not in _CANDIDATE_AUTOMATION_IDS:
                                return 0

                            if event_id == core.UIA_MenuOpenedEventId:
                                with monitor._state_lock:
                                    monitor._candidate_control = control
                                monitor.request_refresh()
                            elif event_id == core.UIA_MenuClosedEventId:
                                with monitor._state_lock:
                                    monitor._candidate_control = None
                                monitor._publish([])
                        except Exception:
                            pass
                        return 0

                handler = AutomationEventHandler()
                root_element = automation.GetRootElement()
                automation.AddAutomationEventHandler(
                    core.UIA_MenuOpenedEventId,
                    root_element,
                    core.TreeScope_Subtree,
                    None,
                    handler,
                )
                automation.AddAutomationEventHandler(
                    core.UIA_MenuClosedEventId,
                    root_element,
                    core.TreeScope_Subtree,
                    None,
                    handler,
                )

                while True:
                    comtypes.client.PumpEvents(0.03)
                    if not self._refresh_requested.is_set():
                        continue
                    self._refresh_requested.clear()
                    time.sleep(0.012)
                    self._refresh(auto)
        except Exception:
            self._supported = False
            self._publish([])


_monitor = ImeCandidateMonitor()


def start_monitor(emit_callback):
    return _monitor.start(emit_callback)


def request_refresh():
    _monitor.request_refresh()


def get_snapshot():
    return _monitor.snapshot()

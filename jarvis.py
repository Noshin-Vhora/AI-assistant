
import threading
import random
from pathlib import Path

from internet_check import is_Online
from Alert import Alert
from Data.DLG_Data import startup_greeting, offline_dlg
from co_brain import Mujib
from TextToSpeech.Fast_DF_TTS import speak
from Automation.Battery import check_plug
from Time_Operations.throw_alert import check_schedule, check_Alam


PROJECT_ROOT = Path(__file__).resolve().parent
ALAM_PATH = PROJECT_ROOT / "Alam_data.txt"
SCHEDULE_PATH = PROJECT_ROOT / "schedule.txt"


def main(stop_event=None):

    if stop_event is None:
        stop_event = threading.Event()

    if not is_Online():
        if not stop_event.is_set():
            Alert(random.choice(offline_dlg))
        return

    try:
        if not stop_event.is_set():
            speak(startup_greeting)

        workers = [
            threading.Thread(
                target=check_plug,
                args=(stop_event,),
                daemon=True
            ),
            threading.Thread(
                target=check_schedule,
                args=(str(SCHEDULE_PATH), stop_event),
                daemon=True
            ),
            threading.Thread(
                target=Mujib,
                args=(stop_event,),
                daemon=True
            ),
            threading.Thread(
                target=check_Alam,
                args=(str(ALAM_PATH), stop_event),
                daemon=True
            ),
        ]

        for worker in workers:
            worker.start()

        while not stop_event.is_set():
            stop_event.wait(0.3)

    except Exception as error:
        print("MUJIB main error:", error)

    finally:
        stop_event.set()

        print("Stopping MUJIB background services...")

        for worker in workers:
            worker.join(timeout=5)

        print("MUJIB main stopped.")


if __name__ == "__main__":
    main()

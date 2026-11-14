
import threading
import time
from pathlib import Path

from Automation.device_access import execute_device_command
from NetHyTechSTT.listen import listen
from TextToSpeech.Fast_DF_TTS import speak
from Brain.brain import Main_Brain

from Time_Operations.brain import input_manage, input_manage_Alam
from Features.create_file import create_file

from Vision.Vbrain import *
from Vision.MVbrain import *

from Weather_Check.check_weather import get_weather_by_address
from Whatsapp_automation.wa import send_msg_wa
from TextToImage.gen_image import generate_image

from Features.mike_health import mike_health
from Features.speaker_health import speaker_health_test
from Features.br_persentage import check_br_persentage
from Features.set_br import set_brightness_windows
from Features.set_get_volume import *
from Features.check_running_app import *


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_ROOT / "input.txt"
LOG_FILE = PROJECT_ROOT / "log.txt"

speaking_event = threading.Event()

numbers = [
    "1:", "2:", "3:", "4:", "5:",
    "6:", "7:", "8:", "9:"
]


def clear_file():
    INPUT_FILE.write_text("", encoding="utf-8")


def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write("\n" + str(message))


def speak_response(response, stop_event=None):

    if not response:
        return

    if stop_event and stop_event.is_set():
        return

    print("MUJIB:", response)
    log_message("MUJIB: " + str(response))

    speaking_event.set()

    try:
        if not stop_event or not stop_event.is_set():
            speak(response)
    finally:
        speaking_event.clear()


def process_input(output_text, stop_event=None):

    output_text = output_text.strip().lower()

    if not output_text:
        return

    if stop_event and stop_event.is_set():
        return

    print("Processing:", output_text)
    log_message("You: " + output_text)

    
    if output_text in ("stop mujib", "exit mujib", "close mujib","chup"):
        if stop_event:
            stop_event.set()
        return

    
    if output_text.startswith("tell me"):

        output_text = output_text.replace(" p.m.", "PM")
        output_text = output_text.replace(" a.m.", "AM")

        if "11:" in output_text or "12:" in output_text:
            input_manage(output_text)
        else:
            for number in numbers:
                if number in output_text:
                    output_text = output_text.replace(
                        number, f"0{number}"
                    )
                    input_manage(output_text)
                    break
        return

   
    if output_text.startswith("set alarm"):

        output_text = output_text.replace(" p.m.", "PM")
        output_text = output_text.replace(" a.m.", "AM")

        if "11:" in output_text or "12:" in output_text:
            input_manage_Alam(output_text)
        else:
            for number in numbers:
                if number in output_text:
                    output_text = output_text.replace(
                        number, f"0{number}"
                    )
                    input_manage_Alam(output_text)
                    break
        return

   
    device_response = execute_device_command(output_text)

    if device_response is not None:
        speak_response(device_response, stop_event)
        return

    
    if output_text.startswith("create") and "file" in output_text:
        create_file(output_text)
        return

   
    if "what is this" in output_text or "what can you see" in output_text:

        image_path = str(PROJECT_ROOT / "captured_image.png")

        if capture_image_and_save(image_path):
            encoded_image = encode_image_to_base64(image_path)
            answer = vision_brain(encoded_image)
            speak_response(answer, stop_event)

        return

    if (
        "what is in front of mobile camera" in output_text
        or "what can you see use mobile camera" in output_text
    ):

        image_path = str(PROJECT_ROOT / "captured_image.png")

        if capture_image_and_save(image_path):
            encoded_image = encode_image_to_base64(image_path)
            answer = mobile_vision_brain(encoded_image)
            speak_response(answer, stop_event)

        return

    
    if "check weather" in output_text:
        location = output_text.replace(
            "check weather in", ""
        ).strip()

        answer = get_weather_by_address(location)
        speak_response(answer, stop_event)
        return


    if "send message on whatsapp" in output_text:
        send_msg_wa()
        return

  
    if "generate image" in output_text:
        prompt = output_text.replace(
            "generate image", ""
        ).strip()

        generate_image(prompt)
        speak_response(
            "Image generation request completed.",
            stop_event
        )
        return

  
    if (
        "check mike" in output_text
        or "check mike health" in output_text
        or "check microphone" in output_text
    ):
        mike_health()
        return

    if "check speaker health" in output_text or "check speaker" in output_text:
        speaker_health_test()
        return

    
    if "check brightness percentage" in output_text:
        check_br_persentage()
        return

    if "set brightness percentage" in output_text:
        value = output_text.replace(
            "set brightness percentage", ""
        ).strip()

        set_brightness_windows(int(value))
        return


    if "check volume level" in output_text:
        get_volume_windows()
        return

    if "set volume level" in output_text:
        value = (
            output_text.replace("set volume level", "")
            .replace("%", "")
            .strip()
        )

        set_volume_windows(int(value))
        return

    
    if "check running application" in output_text:
        check_running_app()
        return

  
    response = Main_Brain(output_text)
    speak_response(response, stop_event)


def check_inputs(stop_event):

    last_text = ""
    last_change_time = time.time()

    while not stop_event.is_set():

        try:
            if INPUT_FILE.exists():

                input_text = INPUT_FILE.read_text(
                    encoding="utf-8"
                ).strip().lower()

                if input_text and input_text != last_text:
                    last_text = input_text
                    last_change_time = time.time()

                if (
                    input_text
                    and time.time() - last_change_time >= 1.2
                ):
                    try:
                        process_input(input_text, stop_event)
                    except Exception as error:
                        print("MUJIB Processing Error:", error)

                    clear_file()
                    last_text = ""

            time.sleep(0.15)

        except Exception as error:
            print("MUJIB Input Error:", error)
            time.sleep(0.5)


def Mujib(stop_event=None):

    if stop_event is None:
        stop_event = threading.Event()

    clear_file()
    print("_____ MUJIB STARTED _____")

    t1 = threading.Thread(
        target=listen,
        args=(speaking_event, stop_event),
        daemon=True
    )

    t2 = threading.Thread(
        target=check_inputs,
        args=(stop_event,),
        daemon=True
    )

    t1.start()
    t2.start()

    while not stop_event.is_set():
        time.sleep(0.2)

    print("MUJIB shutdown requested.")

    speaking_event.clear()

    
    t1.join(timeout=5)
    t2.join(timeout=2)

    clear_file()
    print("_____ MUJIB STOPPED _____")

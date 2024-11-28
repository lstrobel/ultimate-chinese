import os
import logging
from typing import Callable, Optional, TypeVar
import azure.cognitiveservices.speech as speechsdk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class AzureApiWrapper:
    """Wrapper for Azure API calls with retry logic"""

    def __init__(self, max_tries: int = 3):
        self.max_tries = max_tries
        self.logger = logging.getLogger(__name__)

    def execute_with_retry(
        self,
        operation: Callable[[], T],
        error_callback: Optional[Callable[[Exception, int], None]] = None,
    ) -> Optional[T]:
        """
        Execute an operation with retry logic

        Args:
            operation: The function to execute
            error_callback: Optional callback for error handling

        Returns:
            The result of the operation if successful, None otherwise
        """
        for attempt in range(self.max_tries):
            try:
                return operation()
            except Exception as e:
                if error_callback:
                    error_callback(e, attempt)
                if attempt == self.max_tries - 1:
                    self.logger.error(f"All {self.max_tries} attempts failed")
                    return None


class TTSGenerator:
    """Class to handle audio generation using Azure Speech Services"""

    def __init__(
        self,
        ssml_template_path: str,
        voice_name: str = "zh-CN-XiaoxiaoNeural",
        max_tries: int = 1,
    ):
        """Initialize with voice name and SSML template path"""
        self.ssml_template_path = ssml_template_path
        self.voice_name = voice_name
        self.speech_config = self._setup_speech_config()
        self.api_wrapper = AzureApiWrapper(max_tries=max_tries)

    def _setup_speech_config(self):
        """Configure Azure Speech Service with the specified voice"""
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("AZURE_SPEECH_KEY"), region="eastus"
        )
        speech_config.speech_synthesis_voice_name = self.voice_name
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
        )
        return speech_config

    def generate_audio(self, pinyin_sapi: str, output_path: str) -> bool:
        """Generate audio file for the given text using SSML template"""
        # Configure audio output and synthesizer
        audio_config = speechsdk.AudioConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

        # Load and format SSML template
        with open(self.ssml_template_path, "r", encoding="utf-8") as f:
            ssml_string = f.read().format(pinyin_sapi=pinyin_sapi)

        def synthesis_operation():
            result = synthesizer.speak_ssml_async(ssml_string).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Generated audio for: {pinyin_sapi}")
                return True

            if result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                if details.reason == speechsdk.CancellationReason.Error:
                    error_msg = details.error_details
                    if "429" in error_msg:
                        raise RuntimeError("Azure rate limit exceeded")
                    raise RuntimeError(f"Speech synthesis failed: {error_msg}")
            return False

        return bool(
            self.api_wrapper.execute_with_retry(
                synthesis_operation,
                lambda e, a: logger.warning(f"Attempt {a + 1} failed: {str(e)}"),
            )
        )

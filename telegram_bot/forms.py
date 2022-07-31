import datetime
from typing import Optional

from django import forms

from . import consts, models


class BeatUserSettingsForm(forms.ModelForm):
    minute_step: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_field = self.Meta.fields[0]
        self.fields[self.main_field].required = True

    def _clean_main_field(self) -> datetime.time:
        cd_main_field: datetime.time = self.cleaned_data.get(self.main_field)
        if cd_main_field:
            minute: int = cd_main_field.minute or 60
            if minute % self.minute_step != 0:
                self.add_error(self.main_field, f"Minutes must be a multiple of {self.minute_step}")
        return cd_main_field

    def get_error_message(self):
        if not self.errors:
            return ""
        return "\n".join([str(error.message) for error in self.errors[self.main_field].data])

    class Meta:
        model = models.TelegramUserSettings
        fields = "__all__"


class WeatherBeatUserSettingsForm(BeatUserSettingsForm):
    minute_step = consts.WEATHER_MINUTE_STEP_BEAT

    def clean_beat_weather(self):
        return self._clean_main_field()

    class Meta(BeatUserSettingsForm.Meta):
        fields = [
            "beat_weather",
        ]


class CurrencyBeatUserSettingsForm(BeatUserSettingsForm):
    minute_step = consts.CURRENCY_MINUTE_STEP_BEAT

    def clean_beat_currency(self):
        return self._clean_main_field()

    class Meta(BeatUserSettingsForm.Meta):
        fields = [
            "beat_currency",
        ]

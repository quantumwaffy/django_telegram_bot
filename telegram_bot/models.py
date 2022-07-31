from django.db import models


class Timestamp(models.Model):
    created_at = models.DateTimeField("Create datetime", auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField("Update datetime", auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class ActualCurrencyInfo(Timestamp):
    bank = models.CharField(max_length=255, verbose_name="Bank name")
    city = models.CharField(max_length=7, verbose_name="Regional city")
    usd_buy = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Buy USD", null=True)
    usd_sell = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Sale USD", null=True)
    euro_buy = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Buy EUR", null=True)
    euro_sell = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Sale EUR", null=True)
    rub_buy = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Buy RUB", null=True)
    rub_sell = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Sale RUB", null=True)
    usd_buy_from_euro = models.DecimalField(max_digits=4, decimal_places=3, verbose_name="Buy USD from EUR", null=True)
    usd_sell_from_euro = models.DecimalField(
        max_digits=4, decimal_places=3, verbose_name="Sale USD from EUR", null=True
    )

    class Meta:
        verbose_name = "Actual currency info"

    def __str__(self):
        return f"{self.city}_{self.bank}"


class TelegramUser(Timestamp):
    telegram_id = models.CharField(max_length=255, verbose_name="User telegram ID")
    first_name = models.CharField(max_length=255, verbose_name="First name", null=True)  # noqa
    last_name = models.CharField(max_length=255, verbose_name="Last name", null=True)  # noqa
    username = models.CharField(max_length=255, verbose_name="Username", null=True)  # noqa
    city_location = models.CharField(max_length=50, verbose_name="City location", null=True)  # noqa

    class Meta:
        verbose_name = "Telegram user"
        verbose_name_plural = "Telegram users"

    def __str__(self):
        return f"#{self.telegram_id}"


class Message(Timestamp):
    telegram_user = models.ForeignKey(
        TelegramUser, on_delete=models.PROTECT, related_name="messages", verbose_name="User message"
    )
    text = models.TextField(verbose_name="Message text")

    class Meta:
        verbose_name = "User's message"
        verbose_name_plural = "User's messages"

    def __str__(self):
        return self.text


class TelegramUserSettings(Timestamp):
    telegram_user = models.OneToOneField(
        TelegramUser, related_name="settings", verbose_name="User settings", on_delete=models.CASCADE
    )
    beat_weather = models.TimeField(verbose_name="Weather notifications", null=True)
    beat_currency = models.TimeField(verbose_name="Currency notifications", null=True)

    class Meta:
        verbose_name = "User settings"
        verbose_name_plural = "User's settings"

    def __str__(self):
        return f"{self.telegram_user} {self.__class__.__name__}"

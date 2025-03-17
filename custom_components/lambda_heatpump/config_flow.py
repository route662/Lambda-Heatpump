import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv

from .lambda_heatpump_api import detect_lambda_model

DOMAIN = "lambda_heatpump"

class LambdaHeatpumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            model = await detect_lambda_model(user_input[CONF_IP_ADDRESS])
            if model:
                return self.async_create_entry(title=f"Lambda Heatpump ({model})", data=user_input)
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP_ADDRESS): cv.string}),
            errors=errors,
        )

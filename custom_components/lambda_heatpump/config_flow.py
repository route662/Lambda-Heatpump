"""Config flow for Lambda Heatpump integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv

DOMAIN = "lambda_heatpump"

class LambdaHeatpumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lambda Heatpump."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validierung der Eingaben
            try:
                ip_address = user_input[CONF_IP_ADDRESS]
                update_interval = user_input["update_interval"]

                # Beispiel: Verbindung testen (optional)
                # Hier könnte ein Test der Verbindung zur Wärmepumpe erfolgen

                return self.async_create_entry(
                    title=f"Lambda Heatpump ({ip_address})",
                    data=user_input
                )
            except Exception:  # Fange alle Fehler ab, z. B. Verbindungsprobleme
                errors["base"] = "cannot_connect"

        # Zeige das Formular zur Eingabe der IP-Adresse und des Intervalls
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Optional("update_interval", default=30): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Optional("has_heat_circuit_2", default=True): cv.boolean,
                vol.Optional("has_heat_circuit_3", default=True): cv.boolean,
            }),
            errors=errors,
        )

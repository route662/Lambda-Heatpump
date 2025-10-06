# Lambda Heatpump Integration

This is a custom integration for Home Assistant to monitor and retrieve data from Lambda heat pumps via Modbus TCP.

## Features
- Retrieve real-time data such as temperatures, energy consumption, and system status.
- Fully configurable update intervals.
- Persistent Modbus TCP connection to ensure stable communication.

## Installation
### Option 1: Install via [HACS](https://hacs.xyz/)
1. Ensure that [HACS](https://hacs.xyz/) is installed in your Home Assistant setup.
2. Go to **HACS > Integrations**.
3. Click the three dots in the top-right corner and select **Custom repositories**.
4. Add the repository URL: `https://github.com/route662/Lambda-Heatpump` and select **Integration** as the category.
5. Search for "Lambda Heatpump" in HACS and install the integration.
6. Restart Home Assistant.
7. Add the integration via the Home Assistant UI and configure the IP address and update interval.

### Option 2: Manual Installation
1. Download the repository as a ZIP file and extract it.
2. Copy the `lambda_heatpump` folder to your Home Assistant `custom_components` directory.
3. Restart Home Assistant.
4. Add the integration via the Home Assistant UI and configure the IP address and update interval.

## Acknowledgments
Special thanks to **Ralf Winter** for his contributions and inspiration for this integration.

For more information about Lambda heat pumps and their Modbus protocol, visit:
- [Lambda Heatpump Website](https://lambda-wp.at)
- [Modbus Documentation (PDF)](https://lambda-wp.at/wp-content/uploads/2025/02/Modbus-Beschreibung-und-Protokoll.pdf)

## Logo
The logo used in this project is the property of Lambda Wärmepumpen and is used here for informational purposes only. For more details, visit [Lambda Heatpump Website](https://lambda-wp.at).

## Support
If you find this integration helpful, consider supporting me:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-yellow)](https://www.buymeacoffee.com/route662)

## License
This project is licensed under the GNU General Public License v3. See the [LICENSE](LICENSE) file for details.

# Lambda Wärmepumpen Integration

Dies ist eine benutzerdefinierte Integration für Home Assistant, um Daten von Lambda Wärmepumpen über Modbus TCP zu überwachen und abzurufen.

## Funktionen
- Echtzeitdaten wie Temperaturen, Energieverbrauch und Systemstatus abrufen.
- Vollständig konfigurierbare Abfrageintervalle.
- Persistente Modbus-TCP-Verbindung für stabile Kommunikation.

## Installation
### Option 1: Installation über [HACS](https://hacs.xyz/)
1. Stelle sicher, dass [HACS](https://hacs.xyz/) in deiner Home Assistant-Installation eingerichtet ist.
2. Gehe zu **HACS > Integrationen**.
3. Klicke oben rechts auf die drei Punkte und wähle **Benutzerdefinierte Repositories**.
4. Füge die Repository-URL `https://github.com/route662/Lambda-Heatpump` hinzu und wähle **Integration** als Kategorie.
5. Suche in HACS nach "Lambda Wärmepumpe" und installiere die Integration.
6. Starte Home Assistant neu.
7. Füge die Integration über die Benutzeroberfläche von Home Assistant hinzu und konfiguriere die IP-Adresse sowie das Abfrageintervall.

### Option 2: Manuelle Installation
1. Lade das Repository als ZIP-Datei herunter und entpacke es.
2. Kopiere den Ordner `lambda_heatpump` in das Verzeichnis `custom_components` deiner Home Assistant-Installation.
3. Starte Home Assistant neu.
4. Füge die Integration über die Benutzeroberfläche von Home Assistant hinzu und konfiguriere die IP-Adresse sowie das Abfrageintervall.

## Danksagungen
Besonderer Dank gilt **Ralf Winter** für seine Beiträge und Inspiration zu dieser Integration.

Weitere Informationen zu Lambda Wärmepumpen und deren Modbus-Protokoll findest du hier:
- [Lambda Wärmepumpen Webseite](https://lambda-wp.at)
- [Modbus-Dokumentation (PDF)](https://lambda-wp.at/wp-content/uploads/2025/02/Modbus-Beschreibung-und-Protokoll.pdf)

## Logo
Das in diesem Projekt verwendete Logo ist Eigentum von Lambda Wärmepumpen und wird hier nur zu Informationszwecken verwendet. Weitere Informationen findest du auf der [Lambda Wärmepumpen Webseite](https://lambda-wp.at).

## Unterstützung
Wenn dir diese Integration hilft, kannst du mich gerne unterstützen:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-yellow)](https://www.buymeacoffee.com/route662)

## Lizenz
Dieses Projekt steht unter der GNU General Public License v3. Siehe die Datei [LICENSE](LICENSE) für weitere Details.
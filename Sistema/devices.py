# devices.py
import paho.mqtt.client as mqtt

class Device:
    def __init__(self, name, command_topic):
        self.name = name
        self.command_topic = command_topic

    def send_command(self, client, command):
        """
        Envia um comando MQTT ('on' ou 'off') para o dispositivo.
        """
        try:
            result = client.publish(self.command_topic, command)
            status = result.rc  # Código de retorno
            if status == mqtt.MQTT_ERR_SUCCESS:
                return f"Comando '{command}' enviado para {self.name} com sucesso!"
            else:
                return f"Falha ao enviar comando para {self.name}. Código de erro: {status}"
        except Exception as e:
            return f"Erro ao enviar comando para {self.name}: {e}"

    def turn_on(self, client):
        return self.send_command(client, "on")

    def turn_off(self, client):
        return self.send_command(client, "off")

def get_devices():
    return [
        Device("Luz da Sala", "home/luz_sala/comando"),
        Device("Ventilador", "home/ventilador/comando"),
        Device("Termostato", "home/termometro/comando"),
    ]

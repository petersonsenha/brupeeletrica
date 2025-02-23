import streamlit as st
import paho.mqtt.client as mqtt
from devices import get_devices
import ssl
import os
import atexit

# Configurações do Broker MQTT Online
BROKER_ADDRESS = "e955b7463a5c48d49825507c2e7b78dd.s1.eu.hivemq.cloud"  # Seu Cluster URL
BROKER_PORT = 8883  # Porta TLS
KEEPALIVE = 60

# Credenciais MQTT
MQTT_USERNAME = "seu_username"  # Substitua pelo seu username
MQTT_PASSWORD = "sua_password"  # Substitua pela sua password

# Caminho para o certificado CA
CA_CERTS_PATH = os.path.join("certs", "ca_certificate.pem")  # Caminho relativo

# Função de callback para logs (opcional, útil para depuração)
def on_log(client, userdata, level, buf): 
    st.write(f"LOG: {buf}")

# Função para conectar ao broker MQTT
def connect_mqtt():
    client = mqtt.Client()
    
    # Definir credenciais
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Configurar TLS
    try:
        client.tls_set(
            ca_certs=CA_CERTS_PATH,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None
        )
    except Exception as e:
        st.error(f"Erro ao configurar TLS: {e}")
        return None
    
    client.tls_insecure_set(False)  # Garantir que a verificação do certificado está ativa

    # Habilitar logs (opcional)
    client.on_log = on_log
    client.enable_logger()

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, KEEPALIVE)
        return client
    except Exception as e:
        st.error(f"Não foi possível conectar ao broker MQTT: {e}")
        return None

# Função para desconectar o cliente MQTT
def disconnect_mqtt():
    if 'mqtt_client' in st.session_state:
        mqtt_client = st.session_state['mqtt_client']
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            st.session_state['mqtt_client'] = None
            st.write("Cliente MQTT desconectado.")

# Registrar a função de desconexão no atexit
@atexit.register
def cleanup():
    disconnect_mqtt()

# Inicializar o cliente MQTT na sessão do Streamlit
if 'mqtt_client' not in st.session_state:
    mqtt_client = connect_mqtt()
    st.session_state['mqtt_client'] = mqtt_client
    if mqtt_client:
        mqtt_client.loop_start()  # Inicia o loop MQTT

st.title("Controle de Dispositivos via MQTT (Broker Online)")

mqtt_client = st.session_state['mqtt_client']

if mqtt_client is not None:
    # Obter a lista de dispositivos
    devices = get_devices()
    device_names = [device.name for device in devices]

    # Selecionar um dispositivo
    selected_device_name = st.selectbox("Escolha um dispositivo para controlar:", device_names)

    # Encontrar o dispositivo selecionado
    selected_device = next((device for device in devices if device.name == selected_device_name), None)

    if selected_device:
        st.write(f"**Controle do dispositivo:** {selected_device.name}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Ligar"):
                result = selected_device.turn_on(mqtt_client)
                st.success(result)

        with col2:
            if st.button("Desligar"):
                result = selected_device.turn_off(mqtt_client)
                st.warning(result)
    else:
        st.error("Dispositivo selecionado não encontrado.")
else:
    st.error("Aplicação não pode funcionar sem conexão ao broker MQTT.")

# Adicionar um botão para desconectar manualmente (opcional)
if st.button("Desconectar MQTT"):
    disconnect_mqtt()

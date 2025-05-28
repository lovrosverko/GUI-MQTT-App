import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt
import threading
import time

# --- MQTT Konfiguracija ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "PazinGUIClient_Py" + str(int(time.time())) # Jedinstveni ID
MQTT_TOPIC_TEMP = "pazin/temperatura"
MQTT_TOPIC_VENTILATOR_CONTROL = "pazin/ventilator/kontrola"
MQTT_TOPIC_AUTOMATIKA_CONTROL = "pazin/automatika"

# --- Glavna GUI Klasa ---
class MqttControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Pazin Ventilacija i Temperatura")
        master.geometry("450x450") # Postavljamo fiksnu veličinu prozora
        master.resizable(False, False) # Onemogućavamo promjenu veličine prozora

        self.mqtt_client = None
        self.is_connected = False
        self.automatika_status = "OFF" # Početni status automatike
        self.ventilator_status = "OFF" # Početni status ventilatora
        self.current_temperature = "N/A"

        self.setup_gui()
        self.connect_mqtt() # Pokušaj se automatski spojiti pri pokretanju

    def setup_gui(self):
        # Frame za status veze
        conn_frame = ttk.LabelFrame(self.master, text="MQTT Veza")
        conn_frame.pack(pady=10, padx=10, fill="x")

        self.connect_button = ttk.Button(conn_frame, text="Spoji / Odspoji", command=self.toggle_mqtt_connection)
        self.connect_button.pack(side="left", padx=5, pady=5)

        self.status_label = ttk.Label(conn_frame, text="Status: Odspojen", foreground="red")
        self.status_label.pack(side="left", padx=5, pady=5)

        # Frame za prikaz temperature
        temp_frame = ttk.LabelFrame(self.master, text="Trenutna Temperatura")
        temp_frame.pack(pady=10, padx=10, fill="x")

        self.temp_value_label = ttk.Label(temp_frame, text="N/A °C", font=("Arial", 28, "bold"), foreground="blue")
        self.temp_value_label.pack(pady=10)

        # Frame za kontrolu automatike
        automatika_frame = ttk.LabelFrame(self.master, text="Kontrola Automatike")
        automatika_frame.pack(pady=10, padx=10, fill="x")

        self.automatika_button = ttk.Button(automatika_frame, text="Uključi Automatiku", command=self.toggle_automatika)
        self.automatika_button.pack(side="left", padx=5, pady=5)
        
        self.automatika_status_label = ttk.Label(automatika_frame, text="Status: OFF", foreground="red")
        self.automatika_status_label.pack(side="left", padx=5, pady=5)

        # Frame za kontrolu ventilatora
        ventilator_frame = ttk.LabelFrame(self.master, text="Kontrola Ventilatora")
        ventilator_frame.pack(pady=10, padx=10, fill="x")

        self.ventilator_button = ttk.Button(ventilator_frame, text="Uključi Ventilator", command=self.toggle_ventilator)
        self.ventilator_button.pack(side="left", padx=5, pady=5)
        
        self.ventilator_status_label = ttk.Label(ventilator_frame, text="Status: OFF", foreground="red")
        self.ventilator_status_label.pack(side="left", padx=5, pady=5)

        # Log poruka
        self.log_text = tk.Text(self.master, height=6, state="disabled", wrap="word")
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)

        # Ažuriranje statusa gumba na početku
        self.update_button_states()

    def log_message(self, message):
        """Dodaje poruku u log prozor."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END) # Skrolaj na dno
        self.log_text.config(state="disabled")

    def toggle_mqtt_connection(self):
        """Mijenja stanje veze s MQTT brokerom."""
        if self.is_connected:
            self.disconnect_mqtt()
        else:
            self.connect_mqtt()

    def connect_mqtt(self):
        """Pokušava se spojiti na MQTT broker."""
        if self.mqtt_client is None:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=MQTT_CLIENT_ID)
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            # Pokretanje MQTT loopa u zasebnoj niti
            # To je važno da se GUI ne zaledi dok MQTT čeka poruke
            self.mqtt_client.loop_start() 

        try:
            self.log_message(f"Pokušavam se spojiti na {MQTT_BROKER}:{MQTT_PORT}...")
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            self.log_message(f"Greška pri spajanju: {e}")
            self.set_connection_status(False)

    def disconnect_mqtt(self):
        """Odspaja se s MQTT brokera."""
        if self.mqtt_client and self.is_connected:
            self.log_message("Odspajam se s brokera...")
            self.mqtt_client.disconnect()
            self.set_connection_status(False)
        elif self.mqtt_client:
            self.log_message("Klijent nije spojen.")
            self.set_connection_status(False)
        else:
            self.log_message("MQTT klijent nije inicijaliziran.")

    def on_connect(self, client, userdata, flags, rc):
        """Callback funkcija kada se klijent spoji."""
        if rc == 0:
            self.log_message("Uspješno spojen na MQTT Broker!")
            self.set_connection_status(True)
            # Pretplata na topice nakon spajanja
            client.subscribe(MQTT_TOPIC_TEMP)
            client.subscribe(MQTT_TOPIC_VENTILATOR_CONTROL) # Opcionalno, za sinkronizaciju stanja
            client.subscribe(MQTT_TOPIC_AUTOMATIKA_CONTROL) # Opcionalno, za sinkronizaciju stanja
            self.log_message(f"Pretplaćen na: {MQTT_TOPIC_TEMP}")
            self.log_message(f"Pretplaćen na: {MQTT_TOPIC_VENTILATOR_CONTROL}")
            self.log_message(f"Pretplaćen na: {MQTT_TOPIC_AUTOMATIKA_CONTROL}")
        else:
            self.log_message(f"Neuspješno spajanje, kod rezultata: {rc}")
            self.set_connection_status(False)

    def on_disconnect(self, client, userdata, rc):
        """Callback funkcija kada se klijent odspoji."""
        self.log_message(f"Odspojen s MQTT Brokera. Kod rezultata: {rc}")
        self.set_connection_status(False)

    def on_message(self, client, userdata, msg):
        """Callback funkcija kada se primi poruka."""
        payload = msg.payload.decode('utf-8')
        self.log_message(f"Primljena poruka na '{msg.topic}': {payload}")

        if msg.topic == MQTT_TOPIC_TEMP:
            try:
                temp_val = float(payload)
                self.current_temperature = f"{temp_val:.2f}"
                self.temp_value_label.config(text=f"{self.current_temperature} °C")
            except ValueError:
                self.log_message(f"Nevažeća temperatura: {payload}")
        
        elif msg.topic == MQTT_TOPIC_AUTOMATIKA_CONTROL:
            if payload == "ON":
                self.automatika_status = "ON"
            elif payload == "OFF":
                self.automatika_status = "OFF"
            self.update_button_states() # Ažuriraj stanje gumba za ventilator
            self.automatika_status_label.config(text=f"Status: {self.automatika_status}",
                                                 foreground="green" if self.automatika_status == "ON" else "red")
            self.automatika_button.config(text="Isključi Automatiku" if self.automatika_status == "ON" else "Uključi Automatiku")

        elif msg.topic == MQTT_TOPIC_VENTILATOR_CONTROL:
            if payload == "ON":
                self.ventilator_status = "ON"
            elif payload == "OFF":
                self.ventilator_status = "OFF"
            self.ventilator_status_label.config(text=f"Status: {self.ventilator_status}",
                                                foreground="green" if self.ventilator_status == "ON" else "red")
            self.ventilator_button.config(text="Isključi Ventilator" if self.ventilator_status == "ON" else "Uključi Ventilator")


    def set_connection_status(self, connected):
        """Ažurira prikaz statusa veze."""
        self.is_connected = connected
        if connected:
            self.status_label.config(text="Status: Spojen", foreground="green")
            self.connect_button.config(text="Odspoji")
        else:
            self.status_label.config(text="Status: Odspojen", foreground="red")
            self.connect_button.config(text="Spoji")
        self.update_button_states()

    def update_button_states(self):
        """Ažurira stanje gumba za kontrolu na temelju statusa veze i automatike."""
        if not self.is_connected:
            self.automatika_button.config(state="disabled")
            self.ventilator_button.config(state="disabled")
        else:
            self.automatika_button.config(state="normal")
            
            if self.automatika_status == "ON":
                self.ventilator_button.config(state="disabled", text="Ručno (Automatika ON)")
                self.ventilator_status_label.config(text="Status: Automatski", foreground="blue")
            else:
                self.ventilator_button.config(state="normal", 
                                              text="Isključi Ventilator" if self.ventilator_status == "ON" else "Uključi Ventilator")
                self.ventilator_status_label.config(text=f"Status: {self.ventilator_status}",
                                                    foreground="green" if self.ventilator_status == "ON" else "red")


    def toggle_automatika(self):
        """Mijenja stanje automatike i šalje MQTT poruku."""
        if not self.is_connected:
            messagebox.showerror("Greška", "Niste spojeni na MQTT broker.")
            return

        new_status = "OFF" if self.automatika_status == "ON" else "ON"
        self.mqtt_client.publish(MQTT_TOPIC_AUTOMATIKA_CONTROL, new_status, qos=1)
        self.log_message(f"Poslano na '{MQTT_TOPIC_AUTOMATIKA_CONTROL}': {new_status}")
        # Ažuriranje statusa će se dogoditi u on_message callbacku kada Dasduino potvrdi promjenu
        # Za brži feedback, možemo ovdje postaviti status, ali bolje je čekati potvrdu
        # self.automatika_status = new_status
        # self.update_button_states()


    def toggle_ventilator(self):
        """Mijenja stanje ventilatora i šalje MQTT poruku (samo ako automatika nije ON)."""
        if not self.is_connected:
            messagebox.showerror("Greška", "Niste spojeni na MQTT broker.")
            return
        
        if self.automatika_status == "ON":
            messagebox.showinfo("Informacija", "Ventilator je u automatskom načinu rada. Ne možete ručno upravljati.")
            return

        new_status = "OFF" if self.ventilator_status == "ON" else "ON"
        self.mqtt_client.publish(MQTT_TOPIC_VENTILATOR_CONTROL, new_status, qos=1)
        self.log_message(f"Poslano na '{MQTT_TOPIC_VENTILATOR_CONTROL}': {new_status}")
        # Ažuriranje statusa će se dogoditi u on_message callbacku kada Dasduino potvrdi promjenu
        # self.ventilator_status = new_status


# --- Pokretanje aplikacije ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MqttControlApp(root)
    
    # Prilagođavamo ponašanje pri zatvaranju prozora
    def on_closing():
        if app.mqtt_client:
            app.mqtt_client.loop_stop() # Zaustavi MQTT nit
            app.mqtt_client.disconnect() # Odspoji se
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing) # Pozovi on_closing kada se prozor zatvori
    root.mainloop()
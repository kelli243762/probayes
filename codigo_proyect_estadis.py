import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

# Crear ventana principal
root = tk.Tk()
root.title("Calculadora Estadística")
root.geometry("900x500")
root.configure(bg="#2C2C2C")  # Fondo negro-gris

# Encabezado
encabezado = tk.Label(root, text="Calculadora Estadística", font=("Arial", 16, "bold"), bg="black", fg="white")
encabezado.pack(fill="x", pady=10)

# Notebook para las pestañas
notebook = ttk.Notebook(root)
frame_ic = ttk.Frame(notebook)
frame_pm = ttk.Frame(notebook)

notebook.add(frame_ic, text="Intervalos de Confianza")
notebook.add(frame_pm, text="Pruebas de Medias")
notebook.pack(expand=True, fill="both")


# Función para cargar datos desde archivo
def cargar_datos(entry_widget):
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv"), ("Archivos Excel", "*.xlsx"), ("Archivos Parquet", "*.parquet")])
    if archivo:
        if archivo.endswith(".csv"):
            datos = pd.read_csv(archivo).values.flatten()
        elif archivo.endswith(".xlsx"):
            datos = pd.read_excel(archivo).values.flatten()
        elif archivo.endswith(".parquet"):
            datos = pd.read_parquet(archivo).values.flatten()
        
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, ','.join(map(str, datos)))

def calcular_intervalo():
    try:
        # Validar que los datos no estén vacíos
        datos_texto = entry_datos_ic.get().strip()
        if not datos_texto:
            messagebox.showerror("Error", "Por favor, ingresa los datos de la muestra.")
            return
        
        datos = list(map(float, datos_texto.split(',')))

        # Validar el nivel de confianza
        nivel_confianza_texto = entry_confianza.get().strip()
        if not nivel_confianza_texto:
            messagebox.showerror("Error", "Por favor, ingresa el nivel de confianza.")
            return
        
        nivel_confianza = float(nivel_confianza_texto) / 100

        # Validar el tipo de prueba
        tipo_prueba = combo_prueba_ic.get()
        if tipo_prueba not in ["Z", "t"]:
            messagebox.showerror("Error", "Selecciona un tipo de prueba válido (Z o t).")
            return

        # Calcular estadísticos
        media = np.mean(datos)
        error = stats.sem(datos)

        if tipo_prueba == "Z":
            z = stats.norm.ppf(1 - (1 - nivel_confianza) / 2)
            intervalo = (float(round(media - z * error, 4)), float(round(media + z * error, 4)))
        elif tipo_prueba == "t":
            t = stats.t.ppf(1 - (1 - nivel_confianza) / 2, df=len(datos)-1)
            intervalo = (float(round(media - t * error, 4)), float(round(media + t * error, 4)))

        # Mostrar resultado
        resultado_ic.config(state='normal')
        resultado_ic.delete("1.0", tk.END)
        resultado_ic.insert(tk.END, f"Intervalo de confianza: {intervalo}")
        resultado_ic.config(state='disabled')

        # Generar la gráfica automáticamente
        generar_grafica_ic(datos, intervalo, tipo_prueba)

    except ValueError:
        messagebox.showerror("Error", "Asegúrate de ingresar datos numéricos separados por comas.")
        
# Función para generar la gráfica del intervalo de confianza
def generar_grafica_ic(datos, intervalo, tipo_prueba):
    media = np.mean(datos)
    error = stats.sem(datos)

    plt.figure(figsize=(6,4))
    x = np.linspace(media - 4*error, media + 4*error, 100)
    
    if tipo_prueba == "Z":
        y = stats.norm.pdf(x, media, error)
        titulo = "Distribución Normal (Z)"
    elif tipo_prueba == "t":
        y = stats.t.pdf(x, df=len(datos)-1, loc=media, scale=error)
        titulo = "Distribución t-Student"

    plt.plot(x, y, label=titulo, color='blue')
    
    plt.axvline(intervalo[0], color='red', linestyle='--', label="Límite inferior")
    plt.axvline(intervalo[1], color='green', linestyle='--', label="Límite superior")
    plt.axvline(media, color='black', linestyle='-', label="Media muestral")
    
    plt.title("Intervalo de Confianza")
    plt.xlabel("Valores")
    plt.ylabel("Densidad de probabilidad")
    plt.legend()
    plt.grid()
    
    plt.show()

# Función de ayuda sobre intervalos de confianza
def mostrar_ayuda_ic():
    messagebox.showinfo("Ayuda - Intervalos de Confianza",
                        "Un intervalo de confianza es un rango en el que se espera que esté la verdadera media poblacional.\n"
                        "Las pruebas Z se usan cuando se conoce la desviación estándar poblacional.\n"
                        "Las pruebas t se usan cuando la muestra es pequeña y no se conoce la desviación estándar poblacional.")

# Función para guardar resultados en archivo de texto
def guardar_resultado_ic():
    resultado = resultado_ic.get("1.0", tk.END).strip()
    if resultado:
        with open("resultado_intervalo_confianza.txt", "w") as file:
            file.write(resultado)
        messagebox.showinfo("Guardado", "El resultado ha sido guardado correctamente.")
    else:
        messagebox.showerror("Error", "No hay resultados para guardar.")

# Configuración de la pestaña "Intervalos de Confianza"
ttk.Label(frame_ic, text="Datos de la muestra:").grid(row=0, column=0)
entry_datos_ic = ttk.Entry(frame_ic, width=30)
entry_datos_ic.grid(row=0, column=1)
ttk.Button(frame_ic, text="Cargar Archivo", command=lambda: cargar_datos(entry_datos_ic)).grid(row=0, column=2)

ttk.Label(frame_ic, text="Nivel de confianza (%):").grid(row=0, column=3)
entry_confianza = ttk.Entry(frame_ic, width=10)
entry_confianza.grid(row=0, column=4)

ttk.Label(frame_ic, text="Tipo de prueba:").grid(row=1, column=0)
combo_prueba_ic = ttk.Combobox(frame_ic, values=["Z", "t"], width=5)
combo_prueba_ic.grid(row=1, column=1)

ttk.Button(frame_ic, text="Calcular", command=calcular_intervalo).grid(row=1, column=2)

ttk.Label(frame_ic, text="Resultado del intervalo de confianza:").grid(row=2, column=0)
resultado_ic = tk.Text(frame_ic, height=3, width=40, state='disabled')
resultado_ic.grid(row=2, column=1, columnspan=4)

ttk.Button(frame_ic, text="Guardar en TXT", command=guardar_resultado_ic).grid(row=3, column=0)
ttk.Button(frame_ic, text="Ayuda", command=mostrar_ayuda_ic).grid(row=3, column=1)


def prueba_medias():
    try:
        # Validar que los datos no estén vacíos
        datos_texto = entry_datos_pm.get().strip()
        if not datos_texto:
            messagebox.showerror("Error", "Por favor, ingresa los datos de la muestra.")
            return
        
        datos = list(map(float, datos_texto.split(',')))

        # Validar la hipótesis nula
        h0_texto = entry_hipotesis.get().strip()
        if not h0_texto:
            messagebox.showerror("Error", "Por favor, ingresa la hipótesis nula.")
            return
        
        h0 = float(h0_texto)

        # Validar el tipo de prueba
        tipo_prueba = combo_prueba_pm.get()
        if tipo_prueba not in ["Z", "t"]:
            messagebox.showerror("Error", "Selecciona un tipo de prueba válido (Z o t).")
            return

        media = np.mean(datos)
        error = stats.sem(datos)

        if tipo_prueba == "Z":
            estadístico = round((media - h0) / error, 4)
            p_value = round(2 * (1 - stats.norm.cdf(abs(estadístico))), 4)
        elif tipo_prueba == "t":
            estadístico = round((media - h0) / error, 4)
            p_value = round(2 * (1 - stats.t.cdf(abs(estadístico), df=len(datos)-1)), 4)

        # Mostrar resultado
        resultado_pm.config(state='normal')
        resultado_pm.delete("1.0", tk.END)
        resultado_pm.insert(tk.END, f"Estadístico: {estadístico}\nValor p: {p_value}")
        resultado_pm.config(state='disabled')

    except ValueError:
        messagebox.showerror("Error", "Asegúrate de ingresar datos numéricos separados por comas.")
        
# Función para generar la gráfica de pruebas de medias
def generar_grafica_pm(datos, h0, estadístico, tipo_prueba):
    media = np.mean(datos)
    error = stats.sem(datos)

    plt.figure(figsize=(6, 4))
    x = np.linspace(media - 4 * error, media + 4 * error, 100)

    if tipo_prueba == "Z":
        y = stats.norm.pdf(x, media, error)
        titulo = "Distribución Normal (Z)"
    elif tipo_prueba == "t":
        y = stats.t.pdf(x, df=len(datos)-1, loc=media, scale=error)
        titulo = "Distribución t-Student"

    plt.plot(x, y, label=titulo, color='blue')

    # Resaltar la hipótesis nula (H0)
    plt.axvline(h0, color='orange', linestyle='--', label="Hipótesis Nula (H0)")

    # Resaltar el estadístico de prueba
    plt.axvline(media, color='black', linestyle='-', label="Media muestral")
    plt.axvline(media + estadístico * error, color='red', linestyle='--', label="Estadístico de prueba")

    plt.title("Prueba de Medias")
    plt.xlabel("Valores")
    plt.ylabel("Densidad de probabilidad")
    plt.legend()
    plt.grid()

    plt.show()
    
    # Modificar la función para calcular pruebas de medias y mostrar la gráfica automáticamente
def prueba_medias():
    try:
        datos_texto = entry_datos_pm.get().strip()
        if not datos_texto:
            messagebox.showerror("Error", "Por favor, ingresa los datos de la muestra.")
            return

        datos = list(map(float, datos_texto.split(',')))

        h0_texto = entry_hipotesis.get().strip()
        if not h0_texto:
            messagebox.showerror("Error", "Por favor, ingresa la hipótesis nula.")
            return
        
        h0 = float(h0_texto)

        tipo_prueba = combo_prueba_pm.get()
        if tipo_prueba not in ["Z", "t"]:
            messagebox.showerror("Error", "Selecciona un tipo de prueba válido (Z o t).")
            return

        media = np.mean(datos)
        error = stats.sem(datos)

        if tipo_prueba == "Z":
            estadístico = round((media - h0) / error, 4)
            p_value = round(2 * (1 - stats.norm.cdf(abs(estadístico))), 4)
        elif tipo_prueba == "t":
            estadístico = round((media - h0) / error, 4)
            p_value = round(2 * (1 - stats.t.cdf(abs(estadístico), df=len(datos)-1)), 4)

        resultado_pm.config(state='normal')
        resultado_pm.delete("1.0", tk.END)
        resultado_pm.insert(tk.END, f"Estadístico: {estadístico}\nValor p: {p_value}")
        resultado_pm.config(state='disabled')

        # Generar la gráfica automáticamente
        generar_grafica_pm(datos, h0, estadístico, tipo_prueba)

    except ValueError:
        messagebox.showerror("Error", "Asegúrate de ingresar datos numéricos separados por comas.")


# Función de ayuda sobre pruebas de medias
def mostrar_ayuda_pm():
    messagebox.showinfo("Ayuda - Pruebas de Medias",
                        "Las pruebas de medias permiten determinar si la media de una muestra es significativamente diferente a un valor de referencia.\n"
                        "Las pruebas Z se usan cuando se conoce la desviación estándar poblacional.\n"
                        "Las pruebas t se usan cuando la muestra es pequeña y no se conoce la desviación estándar poblacional.")

# Función para guardar resultados en archivo de texto
def guardar_resultado_pm():
    resultado = resultado_pm.get("1.0", tk.END).strip()
    if resultado:
        with open("resultado_pruebas_medias.txt", "w") as file:
            file.write(resultado)
        messagebox.showinfo("Guardado", "El resultado ha sido guardado correctamente.")
    else:
        messagebox.showerror("Error", "No hay resultados para guardar.")

# Configuración de la pestaña "Pruebas de Medias"
ttk.Label(frame_pm, text="Datos de la muestra:").grid(row=0, column=0)
entry_datos_pm = ttk.Entry(frame_pm, width=30)
entry_datos_pm.grid(row=0, column=1)
ttk.Button(frame_pm, text="Cargar Archivo", command=lambda: cargar_datos(entry_datos_pm)).grid(row=0, column=2)

ttk.Label(frame_pm, text="Hipótesis nula:").grid(row=0, column=3)
entry_hipotesis = ttk.Entry(frame_pm, width=10)
entry_hipotesis.grid(row=0, column=4)

ttk.Label(frame_pm, text="Tipo de prueba:").grid(row=1, column=0)
combo_prueba_pm = ttk.Combobox(frame_pm, values=["Z", "t"], width=5)
combo_prueba_pm.grid(row=1, column=1)

ttk.Button(frame_pm, text="Calcular", command=prueba_medias).grid(row=1, column=2)

ttk.Label(frame_pm, text="Resultados de la prueba:").grid(row=2, column=0)
resultado_pm = tk.Text(frame_pm, height=4, width=40, state='disabled')
resultado_pm.grid(row=2, column=1, columnspan=4)

ttk.Button(frame_pm, text="Guardar en TXT", command=guardar_resultado_pm).grid(row=3, column=0)
ttk.Button(frame_pm, text="Ayuda", command=mostrar_ayuda_pm).grid(row=3, column=1)

root.mainloop()























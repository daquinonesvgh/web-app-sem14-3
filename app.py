import streamlit as st
from datetime import datetime
from pymongo import MongoClient
import os
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError


@st.cache_resource
def init_mongo_connection():
    try:
        # Obtenemos la cadena de conexión guardada de forma segura
        mongo_uri = os.getenv("MONGODB_URI")        
        # Conectamos a MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        return client
    except Exception as e:
        st.error(f"Error al conectar con los servicios de Azure/MongoDB: {e}")
        return None

def query_theaters_by_city(city_name):
    """Consultar teatros en la base de datos sample_mflix por nombre de ciudad"""
    try:
        # Conectar a MongoDB
        client = init_mongo_connection()
        if not client:
            return None

        # Acceder a la base de datos sample_mflix
        db = client.sample_mflix

        # Acceder a la colección de teatros
        theaters_collection = db.theaters

        # Consultar teatros por ciudad
        query = {"location.address.city": city_name}
        theaters = list(theaters_collection.find(query).limit(5))

        # Obtener conteo total
        total_count = theaters_collection.count_documents(query)

        # Cerrar conexión
        client.close()

        return theaters, total_count

    except Exception as e:
        st.error(f"Error al consultar MongoDB: {e}")
        return None, 0



# Título de la app
st.title("Calculadora de IMC de Diego Quinones para el curso de cloud 💪")

st.write("Esta aplicación calcula tu Índice de Masa Corporal (IMC) y determina tu nivel de peso.")

# Entradas de usuario
peso = st.number_input("Ingresa tu peso (kg):", min_value=0.0, format="%.2f")
estatura = st.number_input("Ingresa tu estatura (m):", min_value=0.0, format="%.2f")

# Calcular IMC
if st.button("Calcular IMC"):
    if peso > 0 and estatura > 0:
        imc = peso / (estatura ** 2)

        st.write(f"Tu IMC es: **{imc:.2f}**")

        # Clasificación según la OMS
        if imc < 18.5:
            st.info("Bajo peso 🟡")
        elif 18.5 <= imc < 25:
            st.success("Peso normal ✅")
        elif 25 <= imc < 30:
            st.warning("Sobrepeso 🟠")
        else:
            st.error("Obesidad 🔴")
    else:
        st.warning("Por favor, ingresa valores válidos.")

st.divider()

st.write("Esta aplicación busca teatros en la base de datos sample_mflix de MongoDB por nombre de ciudad.")


# Campo de entrada para la ciudad
city_name = st.text_input("Nombre de la ciudad:", value="Chicago")

# Botón de búsqueda
if st.button("Buscar Teatros"):
    if city_name:
        with st.spinner(f"Buscando teatros en {city_name}..."):
            theaters, total_count = query_theaters_by_city(city_name)

            if theaters:
                st.success(
                    f"Se encontraron {total_count} teatros en {city_name}")
                st.write(f"Mostrando los primeros 5 resultados:")

                for i, theater in enumerate(theaters, 1):
                    with st.expander(f"Teatro #{i}: {theater.get('location', {}).get('address', {}).get('street1', 'Sin dirección')}"):
                        st.write(f"**ID:** {theater.get('_id')}")
                        st.write(f"**Teatro ID:** {theater.get('theaterId')}")
                        st.write(
                            f"**Dirección:** {theater.get('location', {}).get('address', {}).get('street1')}")
                        st.write(
                            f"**Ciudad:** {theater.get('location', {}).get('address', {}).get('city')}")
                        st.write(
                            f"**Estado:** {theater.get('location', {}).get('address', {}).get('state')}")
                        st.write(
                            f"**Código postal:** {theater.get('location', {}).get('address', {}).get('zipcode')}")
            else:
                st.warning(
                    f"No se encontraron teatros en {city_name} o hubo un error en la consulta.")
    else:
        st.warning("Por favor ingresa un nombre de ciudad.")

st.divider()
st.write("Nota: Esta aplicación requiere una conexión a MongoDB Atlas con acceso a la base de datos sample_mflix.")


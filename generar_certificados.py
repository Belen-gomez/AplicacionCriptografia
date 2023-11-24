from base_conductores import BaseDeConductores
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from AC.ac_conductor.ac_conductores import AC_conductor

def GenerarSolicitudCertificado():
    conductores = BaseDeConductores()
    conductores.load_store()
    for item in conductores._data_list:
        id = str(item["id"])
        nombre = item["nombre"]
        consumo = item["consumo"]
        origen = item["ruta_origen"]
        destino = item["ruta_destino"]
        path = "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores/" + id
        with open(path + "/key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        public_key = private_key.public_key()

        
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.USER_ID, id),
        x509.NameAttribute(NameOID.COMMON_NAME, nombre),
        x509.NameAttribute(NameOID.LOCALITY_NAME, origen),
         x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
        ])).add_extension(
            x509.SubjectAlternativeName([
            # Describe what sites we want this certificate for.
            x509.DNSName("hailo.com"),
            x509.DNSName("www.hailo.com"),
            x509.DNSName("subdomain.hailo.com"),
        ]),
        critical=False,).sign(private_key, hashes.SHA256())

        raiz = AC_conductor()
        certificado = raiz.verificar_firma_csr(csr, public_key)
        print(certificado)

        with open(path + "/certificado.pem",
                  "wb") as f:
            f.write(certificado.public_bytes(serialization.Encoding.PEM))

GenerarSolicitudCertificado()


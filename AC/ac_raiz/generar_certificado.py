from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime

def GenerarACRaiz():
        key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,)

        with open( "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/AC/ac_raiz/key.pem", "wb") as f:
           f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Colmenarejo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Hailo"),
        x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
             key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            # Our certificate will be valid for 10 days
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=730)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        # Sign our certificate with our private key
        ).sign(key, hashes.SHA256())

        with open("/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/AC/ac_raiz/certificado.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

GenerarACRaiz()
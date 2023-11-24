from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from AC.ac_raiz.ac_raiz import AC_raiz

def GenerarSolicitudCertificado():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,)

    with open( "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/AC/ac_conductor/key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    public_key = key.public_key()
    
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Provide various details about who we are.
    x509.NameAttribute(NameOID.BUSINESS_CATEGORY, "Conductor"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Colmenarejo"),
    x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
    ])).add_extension(
        x509.SubjectAlternativeName([
        # Describe what sites we want this certificate for.
        x509.DNSName("hailo.com"),
        x509.DNSName("www.hailo.com"),
        x509.DNSName("subdomain.hailo.com"),
    ]),
    critical=False,).sign(key, hashes.SHA256())

    raiz = AC_raiz()
    certificado = raiz.verificar_firma_csr(csr, public_key)
    print(certificado)

    with open("/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/AC/ac_conductor/certificado.pem", "wb") as f:
        f.write(certificado.public_bytes(serialization.Encoding.PEM))

GenerarSolicitudCertificado()


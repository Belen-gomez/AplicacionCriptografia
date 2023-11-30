from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from claves_usuarios import ClavesUsuarios
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from AC.ac_usuario.ac_usuarios import AC_usuario

class Claves():
    def __init__(self, path, id, nombre):
        self.path = path
        self.id = id
        self.nombre = nombre
    
    def CrearClavePrivada(self):
        """
        Crea la clave privada del los usuarios cuando se registran. Depués se guarda la clave pública en una base datos pública.
        """
        private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )

        with open(self.path + "/key.pem", 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        public_key = private_key.public_key()
        bd = ClavesUsuarios()
        pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
        pem = pem.decode('latin-1')
        pem = pem.replace("-----BEGIN PUBLIC KEY-----\n", "")
        pem = pem.replace("\n-----END PUBLIC KEY-----\n", "")
        bd.add_item({"Correo": self.id, "Clave_publica": pem})

        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Provide various details about who we are.
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.id),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.SURNAME, self.nombre),
            x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
        ])).add_extension(
            x509.SubjectAlternativeName([
                # Describe what sites we want this certificate for.
                x509.DNSName("hailo.com"),
                x509.DNSName("www.hailo.com"),
                x509.DNSName("subdomain.hailo.com"),
            ]),
            critical=False, ).sign(private_key, hashes.SHA256())

        usuario = AC_usuario()
        certificado = usuario.verificar_firma_csr(csr, public_key)

        with open(self.path + "/certificado.pem", "wb") as f:
            f.write(certificado.public_bytes(serialization.Encoding.PEM))



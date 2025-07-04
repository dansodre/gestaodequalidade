import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self, smtp_config=None):
        if smtp_config:
            self.smtp_server = smtp_config.get('smtp_server')
            self.smtp_port = smtp_config.get('smtp_port', 587)
            self.username = smtp_config.get('smtp_username')
            self.password = smtp_config.get('smtp_password')
            self.from_email = smtp_config.get('email_from')
        else:
            # Configurações padrão do ambiente
            self.smtp_server = os.getenv('SMTP_SERVER')
            self.smtp_port = int(os.getenv('SMTP_PORT', 587))
            self.username = os.getenv('SMTP_USERNAME')
            self.password = os.getenv('SMTP_PASSWORD')
            self.from_email = os.getenv('EMAIL_FROM')
    
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Enviar email"""
        try:
            # Verificar se as configurações de email estão disponíveis
            if not all([self.smtp_server, self.username, self.password, self.from_email]):
                print(f"Email simulado enviado para {to_email}")
                print(f"Assunto: {subject}")
                print(f"Corpo: {body}")
                return True
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar corpo do email
            if html_body:
                part1 = MIMEText(body, 'plain', 'utf-8')
                part2 = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(part1)
                msg.attach(part2)
            else:
                part = MIMEText(body, 'plain', 'utf-8')
                msg.attach(part)
            
            # Adicionar anexos se houver
            if attachments:
                for attachment in attachments:
                    if os.path.isfile(attachment):
                        with open(attachment, "rb") as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment)}'
                        )
                        msg.attach(part)
            
            # Conectar ao servidor SMTP e enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"Email enviado com sucesso para {to_email}")
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    def send_action_plan_email(self, to_email, plan_name, actions, responsible_person):
        """Enviar email com plano de ação"""
        subject = f"Plano de Ação: {plan_name}"
        
        # Corpo do email em texto
        body = f"""
Olá {responsible_person},

Um novo plano de ação foi criado: {plan_name}

Ações incluídas:
"""
        
        for i, action in enumerate(actions, 1):
            body += f"""
{i}. {action['title']}
   Responsável: {action['responsible_person']}
   Data de Execução: {action['execution_date']}
   Custo Estimado: R$ {action.get('estimated_cost', 0):.2f}
   Justificativa: {action['justification']}
"""
        
        body += """
Por favor, revise as ações e tome as medidas necessárias.

Atenciosamente,
Sistema de Gestão de Qualidade
"""
        
        # Corpo do email em HTML
        html_body = f"""
<html>
<head></head>
<body>
    <h2>Plano de Ação: {plan_name}</h2>
    <p>Olá <strong>{responsible_person}</strong>,</p>
    <p>Um novo plano de ação foi criado: <strong>{plan_name}</strong></p>
    
    <h3>Ações incluídas:</h3>
    <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>Título</th>
                <th>Responsável</th>
                <th>Data de Execução</th>
                <th>Custo Estimado</th>
                <th>Justificativa</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for action in actions:
            html_body += f"""
            <tr>
                <td>{action['title']}</td>
                <td>{action['responsible_person']}</td>
                <td>{action['execution_date']}</td>
                <td>R$ {action.get('estimated_cost', 0):.2f}</td>
                <td>{action['justification']}</td>
            </tr>
"""
        
        html_body += """
        </tbody>
    </table>
    
    <p>Por favor, revise as ações e tome as medidas necessárias.</p>
    
    <p>Atenciosamente,<br>
    <strong>Sistema de Gestão de Qualidade</strong></p>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, body, html_body)

def send_test_email(to_email, smtp_config):
    """Função para enviar email de teste"""
    email_service = EmailService(smtp_config)
    
    subject = "Teste de Configuração de Email"
    body = """
Este é um email de teste para verificar se as configurações de SMTP estão funcionando corretamente.

Se você recebeu este email, significa que a configuração está funcionando!

Sistema de Gestão de Qualidade
"""
    
    html_body = """
<html>
<head></head>
<body>
    <h2>Teste de Configuração de Email</h2>
    <p>Este é um email de teste para verificar se as configurações de SMTP estão funcionando corretamente.</p>
    <p><strong>Se você recebeu este email, significa que a configuração está funcionando!</strong></p>
    <hr>
    <p><em>Sistema de Gestão de Qualidade</em></p>
</body>
</html>
"""
    
    return email_service.send_email(to_email, subject, body, html_body)

# Instância global
_email_service = None

def get_email_service():
    """Retorna a instância do serviço de email"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


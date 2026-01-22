def send_reset_email(to_email:str, reset_token:str) -> None:
    reset_link: str = f"https://yourdomain.com/reset-password?token={reset_token}"
    # Here you would normally send the email using an email service.
    print(f"Sending password reset email to {to_email} with link: {reset_link}")
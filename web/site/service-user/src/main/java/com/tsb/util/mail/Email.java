package com.tsb.util.mail;

import java.util.Map;

import javax.mail.internet.MimeMessage;

import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;

@SuppressWarnings("rawtypes") 
public class Email{
	
	private JavaMailSender javaMailSender;
	private SimpleMailMessage simpleMailMessage;
	

	public void sendMail(String subject, String to, Map vars) {
		String content = this.genMailContent(vars);
		this.sendMail(subject, content, to);
	}
	
	
	public String genMailContent(Map vars) {
//		templateVars.put("constant", Constant.getInstance());
		StringBuffer content = new StringBuffer();
		content.append("<!DOCTYPE html>");
		content.append("<html><head>");  
		content.append("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />");  
		content.append("</head><body>");
		content.append("<div class='border:1px solid #ccc; height: 300px; width: auto'>");  
		content.append("<p> Hi, ");
		content.append(vars.get("username"));
		content.append("</p>");
		content.append("<p><a href=\"");  
        content.append(vars.get("url")+"?code="+vars.get("code"));  
        content.append("\">");  
        content.append("Click link and reset password");   
        content.append("</a></p>");  
        content.append("</div><hr/>");
        content.append("<footer style='float:right'> Gobi &copy; 2015 </footer> ");
        content.append("</body></html>");  
		
		return content.toString();
	}
	
	/**
	 * @方法名: sendMail
	 * @参数名：@param subject 邮件主题
	 * @参数名：@param content 邮件主题内容
	 * @参数名：@param to 收件人Email地址
	 * @描述语: 发送邮件
	 */
	private void sendMail(String subject, String content, String to) {

		try {
			MimeMessage mimeMessage = javaMailSender.createMimeMessage();
			MimeMessageHelper messageHelper = new MimeMessageHelper(
					mimeMessage, true, "UTF-8");
			messageHelper.setFrom("Gobi<" + simpleMailMessage.getFrom() + ">"); // 设置发件人Email
			messageHelper.setSubject(subject); // 设置邮件主题
			messageHelper.setText(content,  true); // 设置邮件主题内容
			messageHelper.setTo(to); // 设定收件人Email
			javaMailSender.send(mimeMessage); // 发送HTML邮件

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public void setSimpleMailMessage(SimpleMailMessage simpleMailMessage) {
		this.simpleMailMessage = simpleMailMessage;
	}

	public void setJavaMailSender(JavaMailSender javaMailSender) {
		this.javaMailSender = javaMailSender;
	}
	

	
}

package com.tsb.util;

import java.io.IOException;
import java.util.Map;

import javax.mail.internet.MimeMessage;

import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.ui.freemarker.FreeMarkerTemplateUtils;

import freemarker.template.Configuration;
import freemarker.template.TemplateException;

public class Email {
	private JavaMailSender javaMailSender;
	private SimpleMailMessage simpleMailMessage;
	private Configuration freemarkerMailConfiguration;
	private String host;
	

	public void sendMail(String subject, String to, String templateName, @SuppressWarnings("rawtypes") Map templateVars) {
		String content = this.genMailContent(templateName, templateVars);
		this.sendMail(subject, content, to);
	}
	
	@SuppressWarnings("unchecked")
	public String genMailContent(String templateName, @SuppressWarnings("rawtypes") Map templateVars) {
		templateVars.put("host", this.host);
		StringBuffer content = new StringBuffer();
		try {
		    content.append(FreeMarkerTemplateUtils.processTemplateIntoString(
		    		freemarkerMailConfiguration.getTemplate(templateName), templateVars));
		} catch (IOException e) {
		    // handle
		} catch (TemplateException e) {
		    // handle
		}
		
		return content.toString();
	}
	
	/**
	 * @方法名: sendMail
	 * @参数名：@param subject 邮件主题
	 * @参数名：@param content 邮件主题内容
	 * @参数名：@param to 收件人Email地址
	 * @描述语: 发送邮件
	 */
	public void sendMail(String subject, String content, String to) {

		try {
			MimeMessage mimeMessage = javaMailSender.createMimeMessage();
			
			MimeMessageHelper messageHelper = new MimeMessageHelper(
					mimeMessage, true, "UTF-8");
			messageHelper.setFrom("烯牛数据<" + simpleMailMessage.getFrom() + ">"); // 设置发件人Email
			messageHelper.setSubject(subject); // 设置邮件主题
			messageHelper.setText(content,  true); // 设置邮件主题内容
			messageHelper.setTo(to); // 设定收件人Email
			javaMailSender.send(mimeMessage); // 发送HTML邮件

		} catch (Exception e) {
			System.out.println("异常信息：" + e);
		}
	}

	// Spring 依赖注入
	public void setSimpleMailMessage(SimpleMailMessage simpleMailMessage) {
		this.simpleMailMessage = simpleMailMessage;
	}

	// Spring 依赖注入
	public void setJavaMailSender(JavaMailSender javaMailSender) {
		this.javaMailSender = javaMailSender;
	}
	
	// Spring 依赖注入
	public void setFreemarkerMailConfiguration(
			Configuration freemarkerMailConfiguration) {
		this.freemarkerMailConfiguration = freemarkerMailConfiguration;
	}

	public String getHost() {
		return host;
	}

	public void setHost(String host) {
		this.host = host;
	}

}

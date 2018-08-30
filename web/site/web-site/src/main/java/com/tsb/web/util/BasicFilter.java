package com.tsb.web.util;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import com.tsb.service.UserService;
import com.tsb.user.model.User;


public class BasicFilter extends HttpServlet implements Filter{
	
	private static final Logger logger = LogManager.getLogger(BasicFilter.class.getName());
	
	private static final long serialVersionUID = -3016363224520108310L;
	
	private UserService userService;

	public UserService getUserService() {
		return userService;
	}

	public void setUserService(UserService userService) {
		this.userService = userService;
	}

	@Override
	public void destroy() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void doFilter(ServletRequest arg0, ServletResponse arg1,
			FilterChain filter) throws IOException, ServletException {

		HttpServletRequest request=(HttpServletRequest)arg0;     
        HttpServletResponse response  =(HttpServletResponse) arg1;   
        HttpSession session = request.getSession();
        
        String[] arr = request.getRequestURI().split("/");
        
        

        if(request.getRequestURL().indexOf("tsb-web")>0){
        	if(request.getRequestURL() == null || arr.length  == 1 || arr.length  == 2 ) {
            	filter(session, request, response);
            }else if(arr[2].indexOf("index.html") > -1 || arr[2].indexOf("index") > -1){
            	 filter(session, request, response);
    		}
        }else{
	        if(request.getRequestURL() == null || arr.length  == 0 || arr.length == 1 ) {
	        	filter(session, request, response);
	        }else if(  arr[1].indexOf("index.html") > -1 
	        		|| arr[1].indexOf("index") > -1
	        		|| arr[1].indexOf("company") > -1
	        		|| arr[1].indexOf("list") > -1
	        		|| arr[1].indexOf("follow") > -1 ){
	        	 filter(session, request, response);
			}
        }
        
		filter.doFilter(arg0, arg1);
	}
		
	private void filter(HttpSession session, HttpServletRequest request,
			  HttpServletResponse response) throws IOException{
		CookieManager cookieManager = new CookieManager(request, response);
		String username = cookieManager.getCookieValue("username");
		String token = cookieManager.getCookieValue("login_token");
		
		if(null == session.getAttribute("user")){
			
 	    	if(username == null || username == ""){
 	    		response.sendRedirect("/login.html"); 
 	    		return;
 	    	}
 			
 	    	String autoLogin = cookieManager.getCookieValue("auto_login");
 	    	if(autoLogin == null || autoLogin == ""){
 	    		response.sendRedirect("/login.html"); 
 	    		return;
 	    	}
 	    	
 	    	User user = userService.getUserSessionByUsername(username);
 	    	
 	    	if(token != null && token.indexOf(user.getPassword()) > -1){
 	    		session.setAttribute("user", user);
 	    	}
 	    	else{
 	    		response.sendRedirect("/login.html"); 
 	    		return;
 	    	}
         }
	
	}
	
		

	@Override
	public void init(FilterConfig arg0) throws ServletException {
		// TODO Auto-generated method stub
		logger.info("init filter");
	}

}

package com.tsb.model.org;

public class OrganizationConf {
	private Integer id;
	private String salt;
	private Boolean coldcall;
	private String coldcallImapServer;
	private Integer coldcallImapPort;
	private String coldcallUsername;
	private String coldcallPassword;
	private Boolean api;
	private String apiUrlPrefix;
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getSalt() {
		return salt;
	}
	public void setSalt(String salt) {
		this.salt = salt;
	}
	public Boolean getColdcall() {
		return coldcall;
	}
	public void setColdcall(Boolean coldcall) {
		this.coldcall = coldcall;
	}
	public String getColdcallImapServer() {
		return coldcallImapServer;
	}
	public void setColdcallImapServer(String coldcallImapServer) {
		this.coldcallImapServer = coldcallImapServer;
	}
	public Integer getColdcallImapPort() {
		return coldcallImapPort;
	}
	public void setColdcallImapPort(Integer coldcallImapPort) {
		this.coldcallImapPort = coldcallImapPort;
	}
	public String getColdcallUsername() {
		return coldcallUsername;
	}
	public void setColdcallUsername(String coldcallUsername) {
		this.coldcallUsername = coldcallUsername;
	}
	public String getColdcallPassword() {
		return coldcallPassword;
	}
	public void setColdcallPassword(String coldcallPassword) {
		this.coldcallPassword = coldcallPassword;
	}
	public Boolean getApi() {
		return api;
	}
	public void setApi(Boolean api) {
		this.api = api;
	}
	public String getApiUrlPrefix() {
		return apiUrlPrefix;
	}
	public void setApiUrlPrefix(String apiUrlPrefix) {
		this.apiUrlPrefix = apiUrlPrefix;
	}
}

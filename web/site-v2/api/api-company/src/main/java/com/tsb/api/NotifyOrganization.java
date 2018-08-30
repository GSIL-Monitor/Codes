package com.tsb.api;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.http.HttpStatus;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.dao.read.company.ArtifactReadDao;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.company.DocumentReadDao;
import com.tsb.dao.read.org.OrganizationConfReadDao;
import com.tsb.dao.read.org.user.DealUserRelReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.model.company.Artifact;
import com.tsb.model.company.Company;
import com.tsb.model.company.Document;
import com.tsb.model.org.Deal;
import com.tsb.model.org.Organization;
import com.tsb.model.org.OrganizationConf;
import com.tsb.model.org.user.DealUserRel;
import com.tsb.model.user.User;
import com.tsb.util.MD5;

@Service
public class NotifyOrganization {
	
	@Autowired
	private OrganizationConfReadDao organizationConfReadDao;
	
	@Autowired
	private CompanyReadDao companyReadDao;
	
	@Autowired
	private ArtifactReadDao artifactReadDao;
	
	@Autowired
	private DealUserRelReadDao dealUserRelReadDao;
	
	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private DocumentReadDao documentReadDao;
	
	@SuppressWarnings({ "unchecked", "rawtypes" })
	public void syncDeal(User sender, Organization org, Deal deal) throws Exception{
		if(deal==null){
			return;
		}
		
		OrganizationConf conf = organizationConfReadDao.get(org.getId());
		if( conf.getApi() == false ){
			return;
		}
		
		Company company = companyReadDao.getById(deal.getCompanyId());
		if( company == null){
			return;
		}
		
		List<Artifact> artifacts = artifactReadDao.getByCompIdAndType(company.getId(), 4010, 0, Integer.MAX_VALUE);
		
		//User assignee = null;
		User sponsor = null;
		/*
		DealUserRel r1 = dealUserRelReadDao.getByDealIdAndIdentify(deal.getId(), 21020);
		if( r1 != null){
			assignee = userReadDao.getById(r1.getUserId());
		}
		*/
		User assignee = sender;
		
		DealUserRel r2 = dealUserRelReadDao.getByDealIdAndIdentify(deal.getId(), 21030);
		if( r2 != null){
			sponsor = userReadDao.getById(r2.getUserId());
		}
		
		List<Document> documents = documentReadDao.listByCompanyIdAndType(company.getId(), 9010);
		
		HashMap data = new HashMap();
		data.put("code", company.getCode());
		MD5 md5 = new MD5();
		String sig = md5.getMD5ofUTF8Str(conf.getSalt() + company.getCode());
		data.put("sig", sig);
		data.put("name", company.getName());
		data.put("fullName", company.getFullName());
		if(company.getDescription() != null && !company.getDescription().trim().isEmpty()){
			data.put("description", company.getDescription());
		}
		else{
			data.put("description", company.getBrief());
		}
		data.put("locationId", company.getLocationId());
		data.put("address", company.getAddress());
		data.put("establishDate", company.getEstablishDate());
		data.put("currency", deal.getCurrency());
		data.put("preMoney", deal.getPreMoney());
		data.put("investment", deal.getInvestment());
		data.put("status",deal.getStatus());
		data.put("declineStatus", deal.getDeclineStatus());
		data.put("priority", deal.getPriority());
		data.put("assignee", assignee!=null?assignee.getEmail():null);
		data.put("sponsor", sponsor!=null?sponsor.getEmail():null);
		data.put("sender", sender==null?null:sender.getEmail());
		ArrayList<String> websites = new ArrayList<String>();
		for(Artifact a : artifacts){
			websites.add(a.getLink());
		}
		data.put("websites", websites);
		ArrayList<Map> bps = new ArrayList<Map>();
		for(Document doc : documents){
			HashMap bp = new HashMap();
			bp.put("name", doc.getName());
			bp.put("link", doc.getLink());
			bps.add(bp);
		}
		data.put("bps", bps);
		
		ObjectMapper mapper = new ObjectMapper();
		String strJson = mapper.writeValueAsString(data);
		System.out.println(strJson);
		
		String apiUrl = conf.getApiUrlPrefix() + "/sync/deal.json";
		CloseableHttpClient httpClient = HttpClients.createDefault();
		HttpPost httpPost = new HttpPost(apiUrl);
		httpPost.addHeader("Content-type","application/json; charset=utf-8");  
		httpPost.setHeader("Accept", "application/json");  
		httpPost.setEntity(new StringEntity(strJson, Charset.forName("UTF-8")));  
		CloseableHttpResponse response = httpClient.execute(httpPost);
		int statusCode = response.getStatusLine().getStatusCode();  
		if (statusCode != HttpStatus.SC_OK) { 
			System.out.println(response.getStatusLine());
		}
		String body = EntityUtils.toString(response.getEntity()); 
		System.out.println(body);
		//Map<String, Object> resp_data = (Map<String, Object>) mapper.readValue(body, Map.class);
	}
}

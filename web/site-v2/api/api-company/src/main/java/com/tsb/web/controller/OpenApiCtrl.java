package com.tsb.web.controller;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.dao.ColdcallVODao;
import com.tsb.company.dao.DealScoreVODao;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.OrganizationConfReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.write.org.DealWriteDao;
import com.tsb.model.company.Company;
import com.tsb.model.org.Deal;
import com.tsb.model.org.OrganizationConf;
import com.tsb.model.user.User;
import com.tsb.util.MD5;

@Controller
@RequestMapping(value = "/api/open/company")
public class OpenApiCtrl extends BaseController {

	@Autowired
	private OrganizationConfReadDao organizationConfReadDao;
	
	@Autowired
	private CompanyReadDao companyReadDao;
	
	@Autowired
	private DealReadDao dealReadDao;
	
	@Autowired
	private DealWriteDao dealWriteDao;
	
	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private ColdcallVODao coldcallVODao;
	
	@Autowired
	private DealScoreVODao dealScoreVODao;
	
	@SuppressWarnings({ "unchecked", "rawtypes" })
	@RequestMapping(value = "/syncstatus", method = RequestMethod.POST)
	@ResponseBody
	public Object syncstatus(@RequestBody String jsonRequest) {
		int returnCode = 0;
		System.out.println(jsonRequest);
		Map map = new HashMap();
		map.put("code", returnCode);
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			String code = (String)data.get("code");
			String sig = (String)data.get("sig");
			Integer organizationId = (Integer)data.get("organizationId");
			if(organizationId == null){
				map.put("code", -2);
				return map;
			}
			
			OrganizationConf conf = organizationConfReadDao.get(organizationId);
			if(conf == null){
				map.put("code", -2);
				return map;
			}
			
			MD5 md5 = new MD5();
			String sig1 = md5.getMD5ofUTF8Str(conf.getSalt() + code);
			if(!sig1.equalsIgnoreCase(sig)){
				map.put("code", -3);
				return map;
			}
			
			Integer declineStatus = (Integer)data.get("declineStatus");
			if( declineStatus == null ){
				map.put("code", -4);
				return map;
			}
			Integer status = (Integer)data.get("status");
			if( status == null ){
				map.put("code", -4);
				return map;
			}
			Integer priority = (Integer)data.get("priority");
			if( priority == null ){
				map.put("code", -4);
				return map;
			}
			if( declineStatus != 18010 && 
				declineStatus != 18020){
				map.put("code", -4);
				return map;
			}
			if( status != 19010 &&
				status != 19020 &&
				status != 19030 &&
				status != 19040 &&
				status != 19050){
				map.put("code", -4);
				return map;
			}
			if( priority != 20010 &&
				priority != 20020 &&
				priority != 20030){
				map.put("code", -4);
				return map;
			}
			
			Company company = companyReadDao.getByCode(code);
			Deal deal = dealReadDao.getByOrganization(company.getId(), organizationId);
			if( deal == null ){
				map.put("code", -5);
				return map;
			}
			deal.setDeclineStatus(declineStatus);
			deal.setStatus(status);
			deal.setPriority(priority);
			deal.setModifyTime(new java.sql.Timestamp(new java.util.Date().getTime()));
			dealWriteDao.update(deal);
		}
		catch(Exception e) {
			e.printStackTrace();
			returnCode = -1;
		}
		
		return map;
	}
	
	@SuppressWarnings({ "unchecked", "rawtypes" })
	@RequestMapping(value = "/scoringreport", method = RequestMethod.POST)
	@ResponseBody
	public Object scoringreport(@RequestBody String jsonRequest) {
		int returnCode = 0;
		System.out.println(jsonRequest);
		Map map = new HashMap();
		map.put("code", returnCode);
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			String fromDateStr = (String)data.get("fromDate");
			String toDateStr = (String)data.get("toDate");
			String sig = (String)data.get("sig");
			Integer organizationId = (Integer)data.get("organizationId");
			if(organizationId == null){
				map.put("code", -2);
				return map;
			}
			
			OrganizationConf conf = organizationConfReadDao.get(organizationId);
			if(conf == null){
				map.put("code", -2);
				return map;
			}
			
			MD5 md5 = new MD5();
			String sig1 = md5.getMD5ofUTF8Str(conf.getSalt() + fromDateStr + toDateStr);
			if(!sig1.equalsIgnoreCase(sig)){
				map.put("code", -3);
				return map;
			}
			
			SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd");
			Date fromDate = sdf.parse(fromDateStr);
			Date toDate = sdf.parse(toDateStr);
			
			ArrayList scores = new ArrayList();
			List<User> users = userReadDao.listByOrgAndRole(organizationId, 25040);
			for(User user : users) {
				if( user.getActive() == 'D') continue;
				HashMap score = new HashMap();
				score.put("name", user.getUsername());
				int cc_assigned_cnt = coldcallVODao.countAssigned(organizationId, user.getId(), fromDate, toDate);
				score.put("cc_assigned_cnt", cc_assigned_cnt);
				int cc_unscored_cnt = coldcallVODao.countTODO(organizationId, user.getId(), 0);
				score.put("cc_unscored_cnt", cc_unscored_cnt);
				
				int rcm_assigned_cnt = dealScoreVODao.countAssigned(organizationId, user.getId(), 23030, fromDate, toDate);
				score.put("rcm_assigned_cnt", rcm_assigned_cnt);
				int rcm_unscored_cnt = dealScoreVODao.countTODO(organizationId, user.getId(), 23030, 0);
				score.put("rcm_unscored_cnt", rcm_unscored_cnt);
				
				scores.add(score);
			}
			
			map.put("scores", scores);	
		}
		catch(Exception e) {
			e.printStackTrace();
			returnCode = -1;
		}
		return map;
	}
}

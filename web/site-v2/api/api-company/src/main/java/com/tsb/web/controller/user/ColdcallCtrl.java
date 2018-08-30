package com.tsb.web.controller.user;

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

import com.tsb.company.service.CompanyService;
import com.tsb.company.service.org.ColdcallForwardService;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.ColdcallCompanyRelReadDao;
import com.tsb.dao.read.org.ColdcallFileReadDao;
import com.tsb.dao.read.org.ColdcallReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.write.org.ColdcallCompanyRelWriteDao;
import com.tsb.dao.write.org.ColdcallWriteDao;
import com.tsb.model.company.Company;
import com.tsb.model.org.Coldcall;
import com.tsb.model.org.ColdcallCompanyRel;
import com.tsb.model.org.ColdcallFile;
import com.tsb.model.org.Organization;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/coldcall")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class ColdcallCtrl extends BaseController {

	@Autowired
	private OrganizationReadDao organizationReadDao;

	@Autowired
	private ColdcallReadDao coldcallReadDao;

	@Autowired
	private ColdcallFileReadDao coldcallFileReadDao;

	@Autowired
	private CompanyReadDao companyReadDao;

	@Autowired
	private ColdcallCompanyRelReadDao coldcallCompanyRelReadDao;

	@Autowired
	private ColdcallWriteDao coldcallWriteDao;

	@Autowired
	private ColdcallCompanyRelWriteDao coldcallCompanyRelWriteDao;

	@Autowired
	private ColdcallForwardService coldcallForwardService;
	
	@Autowired
	private CompanyService companyService;
	
	
	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Object get(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		String code = (String) request.getPayload().get("code");
		ColdcallCompanyRel ccr = coldcallCompanyRelReadDao.getByCompanyId(companyService.get(code).getId());
		Map map = new HashMap();
		map.put("code", 0);
		if(ccr == null){
			return map;
		}
		int coldcallId = ccr.getColdcallId();
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		
		if (coldcall.getOrganizationId() == org.getId()) {
			map.put("coldcall", coldcall);
			List<ColdcallFile> files = coldcallFileReadDao.listByColdcallId(coldcallId);
			map.put("files", files);
		}
		
		return map;
	}

	@RequestMapping(value = "/detail", method = RequestMethod.POST)
	@ResponseBody
	public Object detail(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		Map map = new HashMap();
		if (coldcall.getOrganizationId() == org.getId()) {
			map.put("coldcall", coldcall);
			List<ColdcallFile> files = coldcallFileReadDao.listByColdcallId(coldcallId);
			map.put("files", files);
		}
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/companies", method = RequestMethod.POST)
	@ResponseBody
	public Object listComapnies(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		Map map = new HashMap();
		if (coldcall.getOrganizationId() == org.getId()) {
			List<Company> list = companyReadDao.listByColdcallId(coldcallId);
			map.put("companies", list);
		}
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/candidates", method = RequestMethod.POST)
	@ResponseBody
	public Object listCandidates(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		Map map = new HashMap();
		if (coldcall.getOrganizationId() == org.getId()) {
			List<Company> list = companyReadDao.listCandidatesByColdcallId(coldcallId);
			map.put("candidates", list);
		}
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/select", method = RequestMethod.POST)
	@ResponseBody
	public Object selectCompany4ColdCall(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		Map map = new HashMap();
		if (coldcall.getOrganizationId() == org.getId()) {
			String code = (String) request.getPayload().get("code");
			Company company = companyReadDao.getByCode(code);
			ColdcallCompanyRel rel = coldcallCompanyRelReadDao.getByCompanyIdAndColdcallId(company.getId(), coldcallId);
			if (rel == null) {
				rel = new ColdcallCompanyRel();
				rel.setCompanyId(company.getId());
				rel.setColdcallId(coldcallId);
				rel.setCreateTime(new Date());
				coldcallCompanyRelWriteDao.insert(rel);
			}
		}
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/remove", method = RequestMethod.POST)
	@ResponseBody
	public Object removeCompany4ColdCall(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Organization org = organizationReadDao.getByUser(userId);
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		Coldcall coldcall = coldcallReadDao.get(coldcallId);
		Map map = new HashMap();
		if (coldcall.getOrganizationId() == org.getId()) {
			String code = (String) request.getPayload().get("code");
			Company company = companyReadDao.getByCode(code);
			ColdcallCompanyRel rel = coldcallCompanyRelReadDao.getByCompanyIdAndColdcallId(company.getId(), coldcallId);
			if (rel != null) {
				coldcallCompanyRelWriteDao.delete(rel.getId());
			}
		}
		map.put("code", 0);
		return map;
	}

	@SuppressWarnings("unused")
	@RequestMapping(value = "/decline", method = RequestMethod.POST)
	@ResponseBody
	public Object declineColdCall(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		int coldcallId = (Integer) request.getPayload().get("coldcallId");
		int declineId = (Integer) request.getPayload().get("declineId");
		coldcallWriteDao.decline(coldcallId, declineId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/collegues", method = RequestMethod.POST)
	@ResponseBody
	public Object getCollegues(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		List list = coldcallForwardService.getCollegues(userId);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("list", list);
		return map;
	}

	@RequestMapping(value = "/getForwards", method = RequestMethod.POST)
	@ResponseBody
	public Object getForwards(@RequestBody RequestVO request) {
		Integer coldcallId = (Integer) request.getPayload().get("coldcallId");
		Map map = new HashMap();
		map.put("code", 0);
		map.put("list", coldcallForwardService.getForwards(coldcallId));
		return map;
	}

	@RequestMapping(value = "/forward", method = RequestMethod.POST)
	@ResponseBody
	public Object forward(@RequestBody RequestVO request) {
		
		int userId = request.getUserid();
		int toUserId = (int) request.getPayload().get("forwardUser");
		
		Map map = new HashMap();
		if (toUserId > 0) {
			int coldcallId = (int) request.getPayload().get("coldcallId");
			coldcallForwardService.forward(coldcallId, userId, toUserId);
			map.put("code", 0);

		} else {
			map.put("code", -1);
		}
		return map;
	}

}

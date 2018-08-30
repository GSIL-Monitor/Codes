package com.tsb.web.controller;

import java.util.ArrayList;
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
import com.tsb.api.NotifyOrganization;
import com.tsb.company.service.CompanyService;
import com.tsb.company.service.FootprintService;
import com.tsb.company.service.FundingService;
import com.tsb.company.service.SectorService;
import com.tsb.company.service.TagService;
import com.tsb.company.vo.CompanyDescVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.model.company.Company;
import com.tsb.model.org.Deal;
import com.tsb.model.org.Organization;
import com.tsb.model.user.User;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class CompanyCtrl extends BaseController {

	@Autowired
	private CompanyService companyService;

	@Autowired
	private FootprintService footprintService;

	@Autowired
	private FundingService fundingService;

	@Autowired
	private CompanyReadDao companyReadDao;

	@Autowired
	private UserReadDao userReadDao;

	@Autowired
	private OrganizationReadDao organizationReadDao;

	@Autowired
	private DealReadDao dealReadDao;

	@Autowired
	private NotifyOrganization notify;

	@Autowired
	private SectorService sectorService;

	@Autowired
	private TagService tagService;

	@RequestMapping(value = "/basic", method = RequestMethod.POST)
	@ResponseBody
	public Object getCompanyByCode(@RequestBody RequestVO request) {
		String code = (String) request.getPayload().get("code");
		CompanyVO company = companyService.get(code);
		Map map = new HashMap();
		if (company == null) {
			map.put("code", -1);
			return map;
		}

		CompanyDescVO companyDesc = new CompanyDescVO();
		List sectorList = new ArrayList();
		List tagList = new ArrayList();
		List footprintList = new ArrayList();
		List fundingList = new ArrayList();
		int companyId = company.getId();
		if (companyId > 0) {
			companyDesc = companyService.getDesc(code);
			sectorList = sectorService.getByCompanyId(companyId);
			tagList = tagService.getTags(companyId);
			footprintList = footprintService.get(companyId);
			fundingList = fundingService.get(companyId);
		}

		map.put("company", company);
		map.put("companyDesc", companyDesc);
		map.put("sectors", sectorList);
		map.put("tags", tagList);
		map.put("footprints", footprintList);
		map.put("fundings", fundingList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/list", method = { RequestMethod.POST })
	@ResponseBody
	public Map getCompaniesByCodes(@RequestBody RequestVO request) {

		List codes = (List) request.getPayload().get("codes");
		List companyList = companyService.getCompaniesByCodes(codes);

		Map map = new HashMap();
		map.put("list", companyList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = { RequestMethod.POST })
	@ResponseBody
	public Map updateCompany(@RequestBody RequestVO request) throws Exception {
		int userId = request.getUserid();

		ObjectMapper mapper = new ObjectMapper();
		String update = mapper.writeValueAsString(request.getPayload().get("update"));
		CompanyVO updateCompany = mapper.readValue(update, CompanyVO.class);

		companyService.update(updateCompany, userId);

		User user = userReadDao.getById(userId);
		Organization org = organizationReadDao.getByUser(userId);
		Company c = companyReadDao.getByCode(updateCompany.getCode());
		Deal deal = dealReadDao.getByOrganization(c.getId(), org.getId());

		try {
			if (deal != null) {
				notify.syncDeal(user, org, deal);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Object getCompanyByName(@RequestBody RequestVO request) {
		String name = (String) request.getPayload().get("name");
		String id = (String) request.getPayload().get("id");
		List<Company> companyList = null;
		if (id.equals("name")) {
			companyList = companyReadDao.getByName(name);
		} else if (id.equals("fullName")) {
			companyList = companyReadDao.getByFullName(name);
		}

		Map map = new HashMap();
		map.put("companies", companyList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/gongshang", method = RequestMethod.POST)
	@ResponseBody
	public Object getGongShangByCode(@RequestBody RequestVO request) {
		Integer id = (Integer) request.getPayload().get("id");
		List list = companyService.getGongShang(id);
		Map map = new HashMap();
		if(list.isEmpty()){
			//工商信息不存在
			map.put("code", -1);
		}
		else{
			map.put("list", list);
			map.put("code", 0);
		}
		return map;
	}

}

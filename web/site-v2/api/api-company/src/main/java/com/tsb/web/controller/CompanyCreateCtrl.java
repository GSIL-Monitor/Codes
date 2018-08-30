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
import com.tsb.company.service.ArtifactService;
import com.tsb.company.service.CompanyService;
import com.tsb.company.service.DemodayService;
import com.tsb.company.service.DocumentService;
import com.tsb.company.service.MemberService;
import com.tsb.company.service.SectorService;
import com.tsb.company.service.TagService;
import com.tsb.company.service.UserDealService;
import com.tsb.dao.read.company.CompanyAliasReadDao;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.model.company.Artifact;
import com.tsb.model.company.Company;
import com.tsb.model.company.CompanyAlias;
import com.tsb.model.company.Document;
import com.tsb.model.company.Member;
import com.tsb.model.org.Deal;
import com.tsb.model.org.Organization;
import com.tsb.model.user.User;
import com.tsb.util.CompanyCreateVOUtil;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/create")
public class CompanyCreateCtrl extends BaseController{
	@Autowired
	private CompanyCreateVOUtil companyCreateVOUtil;
	@Autowired
	private CompanyReadDao companyReadDao;
	@Autowired
	private CompanyAliasReadDao companyAliasReadDao;
	@Autowired
	private MemberService memberService;
	@Autowired
	private UserDealService userDealService;

	@Autowired
	private DocumentService documentService;

	@Autowired
	private ArtifactService artifactService;
	@Autowired
	private TagService tagService;

	@Autowired
	private CompanyService companyService;

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
	private DemodayService demodayService;
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/new", method = { RequestMethod.POST })
	@ResponseBody
	public Map createCompany(@RequestBody RequestVO request) throws Exception {
		Map map = new HashMap();
		int userId = request.getUserid();
		if (userId <= 0) {
			map.put("code", 0);
			return map;
		}

		ObjectMapper mapper = new ObjectMapper();
		Integer coldcallId = (Integer) request.getPayload().get("coldcallId");
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Integer source = (Integer) request.getPayload().get("source");
		
		String comstr = mapper.writeValueAsString(request.getPayload().get("company"));
		Company company = mapper.readValue(comstr, Company.class);
		company.setRoundDesc(companyCreateVOUtil.getRoundDesc(company.getRound()));
		company.setRound(companyCreateVOUtil.parseRound(company.getRound()));

		List<Artifact> productList = new ArrayList<Artifact>();
		List products = (List) request.getPayload().get("productList");
		for (int i = 0, size = products.size(); i < size; i++) {
			String add = mapper.writeValueAsString(products.get(i));
			Artifact artifact = mapper.readValue(add, Artifact.class);
			productList.add(artifact);
		}

		List sectorIds = (List) request.getPayload().get("sectorIds");

		List<Integer> tagIds = (List<Integer>) request.getPayload().get("tagIds");

		String memstr = mapper.writeValueAsString(request.getPayload().get("member"));
		Member member = mapper.readValue(memstr, Member.class);
		CompanyAlias alias = null;
		if (company.getFullName() != null && !"".equalsIgnoreCase(company.getFullName())) {
			alias = companyAliasReadDao.getByName(company.getFullName());
		}
		if (alias == null) {
			alias = companyAliasReadDao.getByName(company.getName());
		}

		if (alias != null) {
			Company c = companyReadDao.getById(alias.getCompanyId());
			map.put("code", -2);
			map.put("company", c);
			return map;
		}
		// add new company, return companyId and sourcecompanyId
		Map createResult = companyService.create(company, userId,source);
		Company resultCompany = (Company) createResult.get("company");
		Integer companyId = resultCompany.getId();
		Integer sourceCompanyId = (Integer) createResult.get("sourceCompanyId");

		// add company member
		if (member != null) {
			memberService.addCompanyMember(member, companyId, userId);
		}

		Organization org = organizationReadDao.getByUser(userId);
		// user deal
		if (coldcallId != null && coldcallId > 0) {
			userDealService.addDeal(companyId, org.getId(), userId, coldcallId);
		}
		// demoday company
		if (null != demodayId && demodayId > 0) {
			demodayService.addDemodayCompany(demodayId, resultCompany.getCode(), userId);
		}
		// sector
		sectorService.addCompanySector(companyId, sectorIds, userId);

		// tags
		if (null != tagIds && tagIds.size() > 1) {
			tagService.addTagRels(companyId, tagIds, userId);
		}

		for (Artifact artifact : productList) {
			// to do domain website
			artifact.setCompanyId(companyId);
			artifact.setCreateUser(userId);
		}
		artifactService.add(productList, sourceCompanyId);

		// document
		ArrayList<Document> docs = new ArrayList<Document>();
		List<Map> files = (List<Map>) request.getPayload().get("files");
		for (Map file : files) {
			// System.out.println(file.get("fileName"));
			// System.out.println(file.get("gridId"));
			Document dv = new Document();
			dv.setCompanyId(companyId);
			dv.setName((String) file.get("fileName"));
			dv.setLink((String) file.get("gridId"));
			dv.setDescription("");
			dv.setType(9010);
			docs.add(dv);
		}
		documentService.add(docs, userId);

		User user = userReadDao.getById(userId);

		Deal deal = dealReadDao.getByOrganization(companyId, org.getId());

		try {
			if(deal != null){
				notify.syncDeal(user, org, deal);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		//add note
		String note = (String) request.getPayload().get("note");
		if(null != note)
			if(note.length() > 0)
				userDealService.modifyDealNote(userId, resultCompany.getCode(), null, note);
		
		map.put("code", 0);
		map.put("company", resultCompany);
		return map;
	}

}

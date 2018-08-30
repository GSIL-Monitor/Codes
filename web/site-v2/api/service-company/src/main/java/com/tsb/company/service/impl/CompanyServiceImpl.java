package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.CompanyVODao;
import com.tsb.company.service.CompanyService;
import com.tsb.company.service.SectorService;
import com.tsb.company.service.TagService;
import com.tsb.company.service.async.KafkaAsync;
import com.tsb.company.util.CompanyUtil;
import com.tsb.company.vo.CompanyDescVO;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.dao.read.company.CompanyAliasReadDao;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.company.GongShangBaseReadDao;
import com.tsb.dao.read.company.SourceCompanyReadDao;
import com.tsb.dao.write.company.CompanyAliasWriteDao;
import com.tsb.dao.write.company.CompanyWriteDao;
import com.tsb.dao.write.source.SourceCompanyWriteDao;
import com.tsb.model.company.Company;
import com.tsb.model.company.CompanyAlias;
import com.tsb.model.company.GongShangBase;
import com.tsb.model.source.SourceCompany;
import com.tsb.util.RandomCodeFactory;

@Service
@EnableAsync
@SuppressWarnings({ "unchecked", "rawtypes" })
public class CompanyServiceImpl implements CompanyService {

	@Autowired
	private CompanyReadDao companyReadDao;

	@Autowired
	private CompanyVODao companyVODao;

	@Autowired
	private CompanyWriteDao companyWriteDao;

	@Autowired
	private CompanyAliasWriteDao companyAliasWriteDao;

	@Autowired
	private CompanyAliasReadDao companyAliasReadDao;

	@Autowired
	private SourceCompanyWriteDao sourceCompanyWriteDao;

	@Autowired
	private KafkaAsync kafkaAsync;

	@Autowired
	private TagService tagService;

	@Autowired
	private SectorService sectorService;

	@Autowired
	private GongShangBaseReadDao gongShangBaseReadDao;
	
	@Autowired
	private SourceCompanyReadDao sourceCompanyReadDao;

	@Override
	public CompanyVO get(String code) {
		return companyVODao.getByCode(code);
	}

	@Override
	public String getName(String code) {
		return companyVODao.getName(code);
	}

	@Override
	public CompanyDescVO getDesc(String code) {
		return companyVODao.getDesc(code);
	}

	@Override
	public List<CompanySearchVO> getCompaniesByIds(List companyIds) {
		List<CompanySearchVO> list = companyVODao.getSearch(companyIds);
		CompanyUtil companyUtil = new CompanyUtil();
		list = companyUtil.sortCompanies(list, companyIds);
		for (CompanySearchVO companyVO : list) {
			if (companyVO != null) {
				companyVO.setTags(tagService.getTags(companyVO.getId()));
				companyVO.setSectors(sectorService.getByCompanyId(companyVO.getId()));
				companyVO.setSources(sourceCompanyReadDao.getByCompanyId(companyVO.getId()));
			}
		}

		return list;
	}

	@Override
	public List<CompanySearchVO> getCompaniesByCodes(List codes) {
		List<CompanySearchVO> list = companyVODao.getSearchByCodes(codes);
		CompanyUtil companyUtil = new CompanyUtil();
		list = companyUtil.sortCompanies(list, codes);
		for (CompanySearchVO companyVO : list) {
			if (companyVO != null) {
				companyVO.setTags(tagService.getTags(companyVO.getId()));
				companyVO.setSectors(sectorService.getByCompanyId(companyVO.getId()));
			}
		}

		return list;
	}

	@Override
	public void update(CompanyVO u, Integer userId) {
		Company c = companyReadDao.getByCode(u.getCode());
		c.setName(u.getName());
		c.setBrief(u.getBrief());
		c.setEstablishDate(u.getEstablishDate());
		c.setLocationId(u.getLocationId());
		c.setLogo(u.getLogo());
		c.setDescription(u.getDescription());

		c.setFullName(u.getFullName());
		c.setHeadCountMin(u.getHeadCountMin());
		c.setHeadCountMax(u.getHeadCountMax());
		c.setInvestment(u.getInvestment());
		c.setCurrency(u.getCurrency());
		c.setPreMoney(u.getPreMoney());
		c.setPostMoney(u.getPostMoney());
		c.setShareRatio(u.getShareRatio() == null ? 0f : u.getShareRatio());
		c.setCompanyStatus(u.getCompanyStatus() == null ? 0 : u.getCompanyStatus());
		c.setFundingType(u.getFundingType() == null ? 0 : u.getFundingType());
		c.setRound(u.getRound() == null ? 0 : u.getRound());
		c.setRoundDesc(u.getRoundDesc());

		c.setVerify('Y');
		c.setActive('Y');
		c.setModifyUser(userId);

		Timestamp time = new Timestamp(System.currentTimeMillis());
		c.setModifyTime(time);

		companyWriteDao.update(c);

		String msg = "{\"type\":\"company\", \"id\":" + c.getId() + "}";
		kafkaAsync.sendMsg(msg);
	}

	@Override
	public Map create(Company company, Integer userId,Integer source) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Company c = company;
		c.setCompanyStatus(2010);
		c.setVerify('Y');
		c.setActive('Y');
		c.setCreateUser(userId);
		c.setConfidence(1.0f);
		c.setCreateTime(time);
		String code = RandomCodeFactory.generateMixed(8); // TODO
		c.setCode(code);

		companyWriteDao.insert(c);
		Integer companyId = c.getId();

		// source_company
		SourceCompany sc = new SourceCompany();
		sc.setCompanyId(companyId);
		sc.setName(c.getName());
		sc.setFullName(c.getFullName());
		sc.setBrief(c.getBrief());
		sc.setDescription(c.getDescription());
		sc.setCurrency(c.getCurrency());
		sc.setPreMoney(c.getPreMoney());
		sc.setInvestment(c.getInvestment());
		sc.setVerify('Y');
		sc.setCreateTime(time);
		if(null==source||0==source){
			source = 13001;
		}
		sc.setSource(source);
		sc.setSourceId(code);

		sourceCompanyWriteDao.insert(sc);
		Integer sourceCompanyId = sc.getId();

		// company_alias
		if (c.getFullName() != null && !"".equals(c.getFullName().trim())) {

			CompanyAlias alias = companyAliasReadDao.getByCompanyIdAndName(companyId, c.getFullName().trim());
			if (alias == null) {
				alias = new CompanyAlias();
				alias.setCompanyId(companyId);
				alias.setName(company.getFullName().trim());
				alias.setType(12010);
				alias.setVerify('Y');
				alias.setActive('Y');
				alias.setCreateUser(userId);
				alias.setCreateTime(time);
				companyAliasWriteDao.insert(alias);
			}
		}
		if (c.getName() != null && !"".equals(c.getName().trim())) {
			CompanyAlias alias = companyAliasReadDao.getByCompanyIdAndName(companyId, c.getName().trim());
			if (alias == null) {
				alias = new CompanyAlias();
				alias.setCompanyId(companyId);
				alias.setName(c.getName().trim());
				alias.setType(12020);
				alias.setVerify('Y');
				alias.setActive('Y');
				alias.setCreateUser(userId);
				alias.setCreateTime(time);
				companyAliasWriteDao.insert(alias);
			}
		}

		Map map = new HashMap();
		map.put("company", c);
		map.put("sourceCompanyId", sourceCompanyId);
		// kafka
		// msg = {"type":"company", "id":company_id}
		String msg = "{\"type\":\"company\", \"id\":" + companyId + "}";
		kafkaAsync.sendMsg(msg);
		return map;
	}

	//
	// // domain
	// if (vo.getDomain() != null && !"".equals(vo.getDomain())) {
	// Domain domain = new Domain();
	// domain.setCompanyId(c.getId());
	// domain.setDomain(vo.getDomain());
	// domain.setVerify('Y');
	// domain.setActive('Y');
	// domain.setCreateUser(userId);
	// domain.setCreateTime(time);
	// domainWriteDao.insert(domain);
	// }
	// if (vo.getColdcallId() > 0) {
	// ColdcallCompanyRel ccr = new ColdcallCompanyRel();
	// ccr.setColdcallId(vo.getColdcallId());
	// ccr.setCompanyId(c.getId());
	// ccr.setCreateTime(time);
	// coldcallCompanyRelWriteDao.insert(ccr);
	// }
	//
	// // documents
	// for (DocumentVO dv : docs) {
	// Document doc = new Document();
	// doc.setCompanyId(vo.getCompanyId());
	// doc.setName(dv.getName());
	// doc.setDescription(dv.getDescription());
	// doc.setLink(dv.getLink());
	// doc.setType(dv.getType());
	// doc.setVerify('Y');
	// doc.setActive('Y');
	// doc.setCreateUser(userId);
	// doc.setConfidence(1.0f);
	// doc.setCreateTime(time);
	// documentWriteDao.insert(doc);
	//
	// SourceDocument sd = new SourceDocument();
	// sd.setSourceCompanyId(sc.getId());
	// sd.setDocumentId(doc.getId());
	// sd.setName(doc.getName());
	// sd.setDescription(doc.getDescription());
	// sd.setLink(doc.getLink());
	// sd.setType(doc.getType());
	// sd.setVerify('Y');
	// sd.setCreateTime(time);
	// sourceDocumentWriteDao.insert(sd);
	// }
	// }

	@Override
	public List getGongShang(Integer companyId) {
		List<CompanyAlias> companyAliasList = companyAliasReadDao.getByCompanyId(companyId);
		List list = new ArrayList();
		if (null != companyAliasList && !companyAliasList.isEmpty()) {
			for (CompanyAlias companyAlias : companyAliasList) {
				GongShangBase gongshang = gongShangBaseReadDao.get(companyAlias.getId());
				if(gongshang != null){
					Map map = new HashMap();
					System.out.println(gongshang.getRegNumber());
					map.put("name", companyAlias.getName());
					map.put("data", gongshang);
					if(list.isEmpty()){
						list.add(map);
					}else{
						Boolean flag = false;
						for(int i=0; i< list.size(); i++){
							Map m = (Map)list.get(i);
							GongShangBase gs = (GongShangBase)m.get("data");
							if(gongshang.getRegNumber().equals(gs.getRegNumber()))
								flag = true;
						}
						if(!flag)
							list.add(map);
					}
//					list.add(map);
				}
			}
		}
		return list;
	}

}

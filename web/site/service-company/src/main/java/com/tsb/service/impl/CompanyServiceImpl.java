package com.tsb.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.dao.read.ArtifactReadDao;
import com.tsb.dao.read.CompanyAliasReadDao;
import com.tsb.dao.read.CompanyMemberRelReadDao;
import com.tsb.dao.read.CompanyReadDao;
import com.tsb.dao.read.CompanyTagRelReadDao;
import com.tsb.dao.read.DomainReadDao;
import com.tsb.dao.read.FootprintReadDao;
import com.tsb.dao.read.FundingReadDao;
import com.tsb.dao.read.JobReadDao;
import com.tsb.dao.read.MemberReadDao;
import com.tsb.dao.read.SourceCompanyReadDao;
import com.tsb.dao.write.CompanyWriteDao;
import com.tsb.model.Artifact;
import com.tsb.model.Company;
import com.tsb.model.CompanyAlias;
import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Domain;
import com.tsb.model.Footprint;
import com.tsb.model.Funding;
import com.tsb.model.Member;
import com.tsb.model.source.SourceCompany;
import com.tsb.model.vo.CompanyHeadVO;
import com.tsb.model.vo.CompanyMemberRelVO;
import com.tsb.model.vo.CompanyTagRelVO;
import com.tsb.model.vo.CompanyVO;
import com.tsb.model.vo.FollowCompany;
import com.tsb.model.vo.MemberExperience;
import com.tsb.service.CompanyService;
import com.tsb.util.CommonParseUtil;

@Service
@SuppressWarnings("rawtypes")
public class CompanyServiceImpl implements CompanyService {

	@Autowired
	private CompanyReadDao companyReadDao;
	@Autowired
	private ArtifactReadDao artifactReadDao;
	@Autowired
	private CompanyTagRelReadDao companyTagRelReadDao;
	@Autowired
	private FundingReadDao fundingReadDao;
	@Autowired
	private FootprintReadDao footprintReadDao;
	@Autowired
	private DomainReadDao domainReadDao;
	@Autowired
	private SourceCompanyReadDao sourceCompanyReadDao;
	@Autowired
	private CompanyAliasReadDao companyAliasReadDao;
	@Autowired
	private CommonParseUtil parseUtil;
	@Autowired
	private MemberReadDao memberReadDao;
	@Autowired
	private CompanyMemberRelReadDao cmrReadDao;
	@Autowired
	private JobReadDao jobReadDao;
	@Autowired
	private CompanyWriteDao companyWriteDao;

	@Override
	public Company get(String code) {
		return companyReadDao.get(code);
	}

	@Override
	public Integer getIdByCode(String code) {
		return companyReadDao.getIdByCode(code);
	}

	@Override
	public CompanyVO getByCode(String code) {
		Integer companyId = companyReadDao.getIdByCode(code);
		CompanyVO companyVO = companyReadDao.getCompanyVO(companyId);
		// companyTagRel
		List<CompanyTagRelVO> tagRelList = companyTagRelReadDao.getByCompanyId(companyId);
		// artifact
		List<Artifact> artifactList = artifactReadDao.getByCompanyId(companyId);
		// funding
		List<Funding> fundingList = fundingReadDao.getByCompanyId(companyId);
		// footprint
		List<Footprint> footprintList = footprintReadDao.getByCompanyId(companyId);
		// domain
		List<Domain> domainList = domainReadDao.getByCompanyId(companyId);
		// sourceCompanies
		List<SourceCompany> sourceCompanyList = sourceCompanyReadDao.getByCompanyId(companyId);
		// compamyAlias
		List<CompanyAlias> companyAliasList = companyAliasReadDao.getByCompanyId(companyId);

		companyVO.setTagRelList(tagRelList);
		companyVO.setArtifactList(artifactList);
		companyVO.setFundingList(fundingList);
		companyVO.setFootprintList(footprintList);
		companyVO.setDomainList(domainList);
		companyVO.setSourceCompanyList(sourceCompanyList);
		companyVO.setCompanyAliasList(companyAliasList);

		return companyVO;

	}

	@Override
	public List<FollowCompany> getFollowCompanies(int userId, List companyIds) {
		// get companies,locationName,followStatus and followDate ，此方法会导致companyId=98这个数据丢失，待究
		// List<FollowCompany> sqlList = companyReadDao.getFollowCompanies(userId, companyIds); 
		List<FollowCompany> sqlList = new ArrayList<FollowCompany>();
		for(int i=0,len=companyIds.size();i<len;i++){
			int companyId=(Integer) companyIds.get(i);
			FollowCompany fc= companyReadDao.getFollowCompany(userId, companyId);
			sqlList.add(fc);
		}
		// get tagRelList including tagName by companyId
		for (FollowCompany follCompany : sqlList) {
			Integer companyId = follCompany.getCompany().getId();
			List<CompanyTagRelVO> tagRelList = companyTagRelReadDao.getByCompanyId(companyId);
			follCompany.setTagRelList(tagRelList);
		}
		List<FollowCompany> resultList = new ArrayList<FollowCompany>();
		HashMap<Integer, Object> hashmap = new HashMap<Integer, Object>();
		// String tags = "";
		// int size = 0;
		for (FollowCompany comp : sqlList) {
			// get short tags
			List<CompanyTagRelVO> tagList = comp.getTagRelList();
			String tags = parseTagList(tagList);
			// tags = "";
			// size = tagList.size() > 5 ? 5 : tagList.size();
			// for (int i = 0; i < size; i++) {
			// tags += tagList.get(i).getTagName() + ",";
			// }
			// if (tagList.size() < 6) {
			// tags = tags.substring(0, tags.length() - 1);
			// }

			comp.getCompany().setDescription(parseUtil.parseDesc(comp.getCompany().getDescription()));

			if (tags.indexOf("null") > -1)
				tags = "";

			comp.setKeywords(tags);
			comp.setTagRelList(null);

			hashmap.put(comp.getCompany().getId(), comp);

		}
		for (int i = 0, length = companyIds.size(); i < length; i++) {
			resultList.add((FollowCompany) hashmap.get(companyIds.get(i)));
		}
		return resultList;
	}

	@Override
	public List getIdsByCompanyCodes(List companyCodes) {
		// List<Integer> compIds = new ArrayList<Integer>();
		// for(String code:companyCodes){
		// int id = companyReadDao.getIdByCode(code);
		// compIds.add(id);
		// }
		List compIds = companyReadDao.getIdsByCodes(companyCodes);
		return compIds;
	}

	@Override
	public List<CompanyVO> getCompanies(List compIdList) {
		List<CompanyVO> cVOs = new ArrayList<CompanyVO>();
		for (int index = 0, length = compIdList.size(); index < length; index++) {
			Integer companyId = (Integer) compIdList.get(index);
			CompanyVO companyVO = companyReadDao.getCompanyVO(companyId);
			// companyTagRel
			List<CompanyTagRelVO> tagRelList = companyTagRelReadDao.getByCompanyId(companyId);
			companyVO.setTagRelList(tagRelList);

			cVOs.add(companyVO);
		}
		for (CompanyVO comp : cVOs) {
			// get short tags
			List<CompanyTagRelVO> tagList = comp.getTagRelList();
			String tags = parseTagList(tagList);
			comp.getCompany().setDescription(parseUtil.parseDesc(comp.getCompany().getDescription()));
			if (tags.indexOf("null") > -1)
				tags = "";
			comp.setKeywords(tags);
			comp.setTagRelList(null);
		}

		return cVOs;
	}

	public String parseTagList(List<CompanyTagRelVO> tagList) {
		String tags = "";
		int size = 0;
		size = tagList.size() > 5 ? 5 : tagList.size();
		for (int i = 0; i < size; i++) {
			tags += tagList.get(i).getTagName() + ",";
		}
		if (tagList.size() > 0 && tagList.size() < 6) {
			tags = tags.substring(0, tags.length() - 1);
		}

		return tags;
	}

	@Override
	public List<CompanyMemberRelVO> getMembers(Integer companyId) {

		List<CompanyMemberRelVO> cmrVOList = new ArrayList<CompanyMemberRelVO>();
		List<CompanyMemberRel> cmrList = companyReadDao.getComMemRelById(companyId);
		for (CompanyMemberRel cmr : cmrList) {
			Member member = memberReadDao.getById(cmr.getMemberId());
			CompanyMemberRelVO cmrVO = new CompanyMemberRelVO();
			cmrVO.setCompanyMemberRel(cmr);
			cmrVO.setMember(member);
			cmrVOList.add(cmrVO);
		}
		return cmrVOList;
	}

	@Override
	public CompanyHeadVO getHeadInfo(Integer userId, Integer companyId) {
		CompanyHeadVO chVO = companyReadDao.getCompanyHeadVO(companyId);
		chVO.setTeamCount(cmrReadDao.count(companyId));
		chVO.setJobCount(jobReadDao.count(companyId));
		// chVO.setNewsCount(newsReadDao.count(companyId));
		// chVO.setRelCount(crReadDao.count(companyId));
		// chVO.userCompanyFollow(ucrReadDao.getByUserIdAndCompanyId(userId,
		// companyId));
		// chVO.setCrowdfundingCount(cfReadDao.countByCompanyId(companyId));
		// chVO.setCompanyId(0);
		return chVO;
	}

	@Override
	public Member getMember(int id) {
		return memberReadDao.getById(id);
	}

	@Override
	public List<MemberExperience> getMemberExperienc(int memberId) {
		List<MemberExperience> meList = cmrReadDao.getMemberExperience(memberId);
		return meList;
	}

	@Override
	public List<Artifact> getArtifacts(int companyId, int artifactType) {
		if (artifactType == 0) {
			return artifactReadDao.getByCompanyId(companyId);
		} else {
			return artifactReadDao.getByCompIdAndType(companyId, artifactType);
		}
	}

	@Override
	public void verify(int companyId, Character verify) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Company company = new Company();
		company.setId(companyId);
		company.setVerify(verify);
		company.setModifyTime(time);
		companyWriteDao.verify(company);

	}

}

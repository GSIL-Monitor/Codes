package com.tsb.company.service.collection.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.CollectionVODao;
import com.tsb.company.dao.CompanyVODao;
import com.tsb.company.service.SectorService;
import com.tsb.company.service.TagService;
import com.tsb.company.service.collection.CollectionService;
import com.tsb.company.util.CompanyUtil;
import com.tsb.company.vo.CollectionVO;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.dao.read.collection.CollectionCompanyRelReadDao;
import com.tsb.dao.read.collection.CollectionReadDao;
import com.tsb.dao.read.collection.CollectionUserRelReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.UserOrganizationRelReadDao;
import com.tsb.dao.read.org.user.DealUserScoreReadDao;
import com.tsb.dao.write.collection.CollectionUserRelWriteDao;
import com.tsb.dao.write.collection.CollectionWriteDao;
import com.tsb.enums.CollectionType;
import com.tsb.model.collection.Collection;
import com.tsb.model.collection.CollectionCompanyRel;
import com.tsb.model.collection.CollectionUserRel;
import com.tsb.model.org.Deal;
import com.tsb.model.org.UserOrganizationRel;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class CollectionServiceImpl implements CollectionService {
	@Autowired
	private CollectionCompanyRelReadDao colCompRelReadDao;
	@Autowired
	private CompanyVODao companyVODao;
	@Autowired
	private TagService tagService;
	@Autowired
	private SectorService sectorService;
	@Autowired
	private CollectionReadDao collectionReadDao;
	@Autowired
	private CollectionWriteDao collectionWriteDao;
	// @Autowired
	// private CompanyService companyService;
	@Autowired
	private CollectionUserRelWriteDao curWriteDao;
	@Autowired
	private CollectionUserRelReadDao curReadDao;
	@Autowired
	private UserOrganizationRelReadDao userOrgRelReadDao;
	@Autowired
	private DealReadDao dealReadDao;
	@Autowired
	private DealUserScoreReadDao dealUserScoreReadDao;
	@Autowired
	private CollectionVODao collectionVODao;

	@Override
	public int countTimeLie(int userId) {
		return colCompRelReadDao.countTimeLine(userId);
	}

	@Override
	public int countCollComp(int collectionId) {
		return colCompRelReadDao.countCollComp(collectionId);
	}

	@Override
	public Map getCollections(Integer userId) {
		Map map = new HashMap();
		// 自定义集合
		map.put("customCols", collectionReadDao.getCustomCols(userId, CollectionType.CUSTOM.getValue()));
		// 系统
		map.put("sysCols", collectionReadDao.getSysCols(userId, CollectionType.SYS.getValue()));
		List<CollectionVO> hotCols = collectionVODao.getHotCols(CollectionType.HOT.getValue());
		for (CollectionVO collectionVO : hotCols) {
			CollectionUserRel cur = curReadDao.getByUserIdColId(userId, collectionVO.getId());
			collectionVO.setActive((cur == null ? 'N' : cur.getActive()));
		}
		// 热门推荐
		map.put("hotCols", hotCols);
		return map;
	}

	@Override
	public Map getTimeLineComp(Integer userId, int start, int pageSize) {
		Map result = new HashMap();
		List list = new ArrayList();
		List<CollectionCompanyRel> ccrList = colCompRelReadDao.getColComRelByUserId(userId, start, pageSize);
		if (null == ccrList || ccrList.isEmpty()) {
			result.put("list", list);
			return result;
		}

		for (CollectionCompanyRel ccr : ccrList) {
			Integer companyId = ccr.getCompanyId();
			Map map = getCompanyBasic(userId, companyId);
			map.put("collection", collectionReadDao.getById(ccr.getCollectionId()));
			map.put("updateTime", ccr.getCreateTime());
			list.add(map);
		}
		result.put("list", list);
		return result;
	}

	@Override
	public Map getCollCompList(Integer collectionId, Integer userId, int start, int pageSize) {
		Map result = new HashMap();
		Collection collection = collectionReadDao.getById(collectionId);
		result.put("collection", collection);
		List list = new ArrayList();
		List<CollectionCompanyRel> ccrList = colCompRelReadDao.getColComRelByCollectionId(collectionId, start,
				pageSize);
		if (null == ccrList || ccrList.isEmpty()) {
			result.put("list", list);
			return result;
		}

		for (CollectionCompanyRel ccr : ccrList) {
			Map map = getCompanyBasic(userId, ccr.getCompanyId());
			map.put("collection", collection);
			map.put("updateTime", ccr.getCreateTime());
			list.add(map);
		}
		result.put("list", list);
		return result;
	}

	@Override
	public void updateCollection(Integer collectionId, Integer userId, Character active) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Collection collection = collectionReadDao.getById(collectionId);
		collection.setActive(active);
		collection.setModifyUser(userId);
		collection.setModifyTime(time);
		collectionWriteDao.update(collection);

	}

	@Override
	public Map getSortCompList(Integer userId, Integer sectorId, Integer locationId, Integer round,
			Integer collectionId, int start, int pageSize) {
		Map result = new HashMap();
		List list = new ArrayList();
		// collectionId 为空，那么在是查timeline表
		if (null == collectionId) {
			List<CollectionCompanyRel> ccrList = colCompRelReadDao.getColComRelByUserId(userId, start, pageSize);
			if (null == ccrList || ccrList.isEmpty()) {
				result.put("list", list);
				return result;
			}
			for (CollectionCompanyRel ccr : ccrList) {
				Integer companyId = ccr.getCompanyId();
				CompanySearchVO companyVO = companyVODao.getSort(companyId, sectorId, locationId, round);
				if (null != companyVO) {
					Map map = new HashMap();
					companyVO.setTags(tagService.getTags(companyId));
					companyVO.setSectors(sectorService.getByCompanyId(companyId));
					map.put("company", companyVO);
					map.put("collection", collectionReadDao.getById(ccr.getCollectionId()));
					list.add(map);
				} else {
					continue;
				}
			}
			result.put("list", list);
			return result;

		} else {
			List<Integer> companyIds = colCompRelReadDao.getCompanyIds(collectionId);
			Collection collection = collectionReadDao.getById(collectionId);
			result.put("collection", collection);
			if (null == companyIds || companyIds.isEmpty()) {
				result.put("list", list);
			}
			List<CompanySearchVO> sortSearchList = companyVODao.getSortSearch(companyIds, sectorId, locationId, round);
			CompanyUtil companyUtil = new CompanyUtil();
			list = companyUtil.sortCompanies(list, companyIds);
			for (CompanySearchVO companyVO : sortSearchList) {
				Map map = new HashMap();
				companyVO.setTags(tagService.getTags(companyVO.getId()));
				companyVO.setSectors(sectorService.getByCompanyId(companyVO.getId()));
				map.put("company", companyVO);
				map.put("collection", collection);
				list.add(map);
			}
			result.put("list", list);
			return result;
		}
	}

	@Override
	public void addCollection(List<Integer> sectors, List<Integer> locations, List<Integer> rounds,
			List<Integer> investors, List<Integer> education, List<Integer> works, String name, int userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Collection collection = new Collection();
		collection.setActive('Y');
		collection.setName(name);
		collection.setType(CollectionType.CUSTOM.getValue());
		collection.setCreateUser(userId);
		collection.setCreateTime(time);
		collectionWriteDao.insert(collection);

		CollectionUserRel collectionUserRel = new CollectionUserRel();
		collectionUserRel.setActive('Y');
		collectionUserRel.setCollectionId(collection.getId());
		collectionUserRel.setCreateUser(userId);
		collectionUserRel.setCreateTime(time);
		collectionUserRel.setUserId(userId);
		curWriteDao.insert(collectionUserRel);
	}

	protected Map getCompanyBasic(Integer userId, Integer companyId) {
		Map map = new HashMap();
		CompanySearchVO companyVO = companyVODao.getById(companyId);
		companyVO.setTags(tagService.getTags(companyId));
		companyVO.setSectors(sectorService.getByCompanyId(companyId));
		map.put("company", companyVO);
		map.put("score", getScore(userId, companyId));
		map.put("source", companyVODao.getSource(companyId));
		return map;
	}

	protected Integer getScore(Integer userId, Integer companyId) {
		UserOrganizationRel userOrgRelList = userOrgRelReadDao.get(userId);
		Deal deal = dealReadDao.getByOrganization(companyId, userOrgRelList.getOrganizationId());
		if (null == deal) {
			return null;
		}
		return dealUserScoreReadDao.getByUserIdAndDealId(userId, deal.getId()).getScore();
	}

	@Override
	public void followCollection(Integer collectionId, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		CollectionUserRel cur = curReadDao.getByUserIdColId(userId, collectionId);
		if (cur == null) {
			CollectionUserRel newCur = new CollectionUserRel();
			newCur.setCreateTime(time);
			newCur.setCreateUser(userId);
			newCur.setCollectionId(collectionId);
			newCur.setUserId(userId);
			newCur.setActive('Y');
			curWriteDao.insert(newCur);
		} else {
			cur.setActive('Y');
			cur.setModifyTime(time);
			cur.setModifyUser(userId);
			curWriteDao.update(cur);
		}

	}

	@Override
	public void unFollowCollection(Integer collectionId, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		CollectionUserRel cur = curReadDao.getByUserIdColId(userId, collectionId);
		cur.setModifyTime(time);
		cur.setModifyUser(userId);
		curWriteDao.update(cur);

	}

	@Override
	public int countSort(Integer userId, Integer sector, Integer location, Integer round, Integer collectionId) {
		if (null == collectionId) {
			// timle line sort company数目
			return colCompRelReadDao.countSort(userId, sector, location, round);

		} else {
			// collection下的数目
			return colCompRelReadDao.countColCompSort(sector, location, round, collectionId);

		}

	}

}

package com.tsb.company.service.impl;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.crawler.dao.read.AlexaReadDao;
import com.crawler.dao.read.AndroidReadDao;
import com.crawler.dao.read.CompanyIndexReadDao;
import com.crawler.dao.read.IOSReadDao;
import com.crawler.model.CompanyIndex;
import com.tsb.company.service.TrendsService;
import com.tsb.enums.ArtifactType;
import com.tsb.enums.Market;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class TrendsServiceImpl implements TrendsService {
	@Autowired
	private CompanyIndexReadDao companyIndexReadDao;
	@Autowired
	private AlexaReadDao alexaReadDao;
	@Autowired
	private AndroidReadDao androidReadDao;
	@Autowired
	private IOSReadDao iOSReadDao;

	@Override
	public Map getTrends(Integer companyId, Integer artifactId, Integer artifactType, Integer expand) {

		CompanyIndex companyIndex = companyIndexReadDao.get(companyId);
		Map map = new HashMap();
		if (null == companyIndex) {
			if (ArtifactType.ANDROID.getValue() == artifactType) {
				map.put("sanliulingList", null);
				map.put("baiduList", null);
				map.put("wandoujiaList", null);
				map.put("myappList", null);
			} else if (ArtifactType.IOS.getValue() == artifactType) {
				map.put("iosList", null);
			} else if (ArtifactType.WEBSITE.getValue() == artifactType) {
				map.put("alexaList", null);
			}
			return map;
		}

		// ANDROID 应用
		if (ArtifactType.ANDROID.getValue() == artifactType) {
			List sanliulingList = null;
			List baiduList = null;
			List wandoujiaList = null;
			List myappList = null;
			int androidId = companyIndex.getAndroid();
			if (0 != androidId) {
				sanliulingList = androidReadDao.getByTypeExpand(androidId, artifactId, Market.SANLIULING.getValue(),
						expand);
				baiduList = androidReadDao.getByTypeExpand(androidId, artifactId, Market.BAIDU.getValue(), expand);
				wandoujiaList = androidReadDao.getByTypeExpand(androidId, artifactId, Market.WANDOUJIA.getValue(),
						expand);
				myappList = androidReadDao.getByTypeExpand(androidId, artifactId, Market.MYAPP.getValue(), expand);
			}

			map.put("sanliulingList", sanliulingList);
			map.put("baiduList", baiduList);
			map.put("wandoujiaList", wandoujiaList);
			map.put("myappList", myappList);
		} else if (ArtifactType.IOS.getValue() == artifactType) {
			List iosList = null;
			int iosId = companyIndex.getIos();
			if (0 != iosId) {
				iosList = iOSReadDao.getByTypeExpand(iosId, artifactId, Market.IOS.getValue(), expand);
			}
			map.put("iosList", iosList);
		} else if (ArtifactType.WEBSITE.getValue() == artifactType) {
			List alexaList = null;
			int alexaId = companyIndex.getAlexa();
			if (0 != alexaId) {
				alexaList = alexaReadDao.getByExpand(alexaId, artifactId, expand);
			}
			map.put("alexaList", alexaList);
		}
		return map;
	}

}

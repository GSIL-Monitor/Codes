package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
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
import com.tsb.company.service.ArtifactService;
import com.tsb.company.vo.ArtifactVO;
import com.tsb.dao.read.company.ArtifactPicReadDao;
import com.tsb.dao.read.company.ArtifactReadDao;
import com.tsb.dao.write.company.ArtifactWriteDao;
import com.tsb.dao.write.source.SourceArtifactWriteDao;
import com.tsb.enums.ArtifactType;
import com.tsb.model.company.Artifact;
import com.tsb.model.source.SourceArtifact;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class ArtifactServiceImpl implements ArtifactService {
	@Autowired
	private ArtifactWriteDao artifactWriteDao;
	@Autowired
	private SourceArtifactWriteDao sourceArtifactWriteDao;

	@Autowired
	private ArtifactReadDao artifactReadDao;

	@Autowired
	private ArtifactPicReadDao artifactPicReadDao;

	@Autowired
	private CompanyIndexReadDao companyIndexReadDao;

	@Autowired
	private IOSReadDao iosReadDao;

	@Autowired
	private AndroidReadDao androidReadDao;

	@Autowired
	private AlexaReadDao alexaReadDao;

	@Override
	public Map getArtifacts(int id, int start, int pageSize) {
		Map map = new HashMap();
		for (ArtifactType type : ArtifactType.values()) {
			Map typeMap = new HashMap();
			List<Artifact> artifactList = null;
			List<ArtifactVO> artifactVOList = new ArrayList<ArtifactVO>();
			artifactList = artifactReadDao.getByCompIdAndType(id, type.getValue(), start, pageSize);
			int count = countArtifactType(id, type.getValue());
			if (null != artifactList && !artifactList.isEmpty()) {
				for (Artifact artifact : artifactList) {
					List pics = artifactPicReadDao.get(artifact.getId());
					ArtifactVO artifactVO = new ArtifactVO();
					artifactVO.setArtifact(artifact);
					artifactVO.setPics(pics);
					artifactVOList.add(artifactVO);
				}
			}
			typeMap.put("list", artifactVOList);
			typeMap.put("count", count);
			map.put(type.getName(), typeMap);
		}
		return map;
	}

	@Override
	public List getArtifactTypeList(int id) {

		return artifactReadDao.getTypes(id);
	}

	@Override
	public int countArtifactType(int id, int type) {
		return artifactReadDao.countByCompanyIdAndType(id, type);
	}

	@SuppressWarnings("unused")
	private List getProductCrawler(Artifact artifact) {
		int companyId = artifact.getCompanyId();
		int artifactId = artifact.getId();
		int type = artifact.getType();

		CompanyIndex companyIndex = companyIndexReadDao.get(companyId);
		if (companyIndex == null)
			return null;

		int tableId = 0;
		List data = new ArrayList();
		if (type == ArtifactType.WEBSITE.getValue()) {
			tableId = companyIndex.getAlexa();
			if (tableId > 0)
				data = alexaReadDao.get(tableId, artifactId);
		} else if (type == ArtifactType.IOS.getValue()) {
			tableId = companyIndex.getIos();
			if (tableId > 0)
				data = iosReadDao.get(tableId, artifactId);
		} else if (type == ArtifactType.ANDROID.getValue()) {
			tableId = companyIndex.getAndroid();
			if (tableId > 0)
				data = androidReadDao.get(tableId, artifactId);
		}

		return data;
	}

	@Override
	public void add(List<Artifact> artifactList, Integer sourceCompanyId) {
		for (Artifact artifact : artifactList) {
			Timestamp time = new Timestamp(System.currentTimeMillis());
			artifact.setActive('Y');
			artifact.setCreateTime(time);
			artifactWriteDao.insert(artifact);
			// source_artifact
			SourceArtifact sa = new SourceArtifact();
			sa.setSourceCompanyId(sourceCompanyId);
			sa.setArtifactId(artifact.getId());
			sa.setName(artifact.getName());
			sa.setDescription(artifact.getDescription());
			sa.setLink(artifact.getLink());
			//4010
			sa.setType(ArtifactType.WEBSITE.getValue());
			sa.setVerify('Y');
			sa.setCreateTime(time);
			sourceArtifactWriteDao.insert(sa);
		}

	}

	@Override
	public ArtifactVO getArtifact(int id) {
		ArtifactVO artifactVO = new ArtifactVO();
		artifactVO.setArtifact(artifactReadDao.getById(id));
		artifactVO.setPics(artifactPicReadDao.get(id));
		return artifactVO;
	}

}

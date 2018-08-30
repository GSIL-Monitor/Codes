package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.TagService;
import com.tsb.dao.read.company.CompanyTagRelReadDao;
import com.tsb.dao.read.company.TagReadDao;
import com.tsb.dao.write.company.CompanyTagRelWriteDao;
import com.tsb.dao.write.company.TagWriteDao;
import com.tsb.model.company.CompanyTagRel;
import com.tsb.model.company.Tag;

@Service
public class TagServiceImpl implements TagService {

	@Autowired
	private CompanyTagRelReadDao ctrReadDao;

	@Autowired
	private CompanyTagRelWriteDao ctrWriteDao;

	@Autowired
	private TagReadDao tagReadDao;

	@Autowired
	private TagWriteDao tagWriteDao;

	@Override
	public void addTagRels(Integer companyId, List<Integer> ids, Integer userId) {

		for (Integer tagId : ids) {
			Tag tag = new Tag();
			tag.setId(tagId);
			addTagRel(companyId, tag, userId);
		}

	}

	@Override
	public void deleteTagRels(Integer companyId, List<Integer> ids, Integer userId) {
		for (Integer id : ids) {
			CompanyTagRel ctr = new CompanyTagRel();
			Timestamp time = new Timestamp(System.currentTimeMillis());
			ctr.setCompanyId(companyId);
			ctr.setTagId(id);
			ctr.setActive('N');
			ctr.setVerify('Y');
			ctr.setModifyTime(time);
			ctr.setModifyUser(userId);
			ctrWriteDao.update(ctr);
		}

	}

	@Override
	public void addTagRel(Integer companyId, Tag tag, Integer userId) {
		int tagId = 0;
		tag.setActive('Y');
		tag.setVerify('Y');
		tag.setCreateUser(userId);
		if (tag.getId() == null) {
			Tag dbTag = tagReadDao.getByName(tag.getName());
			if (dbTag == null) {
				tagWriteDao.insert(tag);
				tagId = tag.getId();
			} else {
				tagId = dbTag.getId();
			}
		} else {
			tagId = tag.getId();
			Tag dbTag = tagReadDao.get(tagId);
			if (dbTag == null) {
				tagWriteDao.insert(tag);
				tagId = tag.getId();
			}
		}

		CompanyTagRel ctr = ctrReadDao.getByCompanyIdAndTagId(companyId, tagId);
		Timestamp time = new Timestamp(System.currentTimeMillis());
		if (ctr == null) {
			ctr = new CompanyTagRel();
			ctr.setCompanyId(companyId);
			ctr.setTagId(tagId);
			ctr.setCreateTime(time);
			ctr.setCreateUser(userId);
			ctr.setVerify('Y');
			ctr.setActive('Y');

			ctrWriteDao.insert(ctr);
		} else {
			ctr.setActive('Y');
			ctr.setVerify('Y');
			ctr.setModifyTime(time);
			ctr.setModifyUser(userId);
			ctrWriteDao.update(ctr);
		}
	}

	@Override
	public void deleteTagRel(Integer companyId, Integer tagId, Integer userId) {
		CompanyTagRel ctr = new CompanyTagRel();
		Timestamp time = new Timestamp(System.currentTimeMillis());
		ctr.setCompanyId(companyId);
		ctr.setTagId(tagId);
		ctr.setActive('N');
		ctr.setVerify('Y');
		ctr.setModifyTime(time);
		ctr.setModifyUser(userId);
		ctrWriteDao.update(ctr);
	}

	@Override
	public List<Tag> getTags(Integer companyId) {
		List<CompanyTagRel> ctrList = ctrReadDao.getByCompanyId(companyId);
		if (ctrList == null || ctrList.size() == 0) {
			return null;
		}

		List tagIds = new ArrayList();
		for (CompanyTagRel ctr : ctrList) {
			tagIds.add(ctr.getTagId());
		}

		List tags = tagReadDao.getByIds(tagIds);

		return tags;
	}

	@Override
	public Tag addTag(String name, Integer userId) {
		Tag dbTag = tagReadDao.getByName(name);
		if (null != dbTag) {
			return dbTag;
		} else {
			Timestamp time = new Timestamp(System.currentTimeMillis());
			Tag tag = new Tag();
			tag.setCreateTime(time);
			tag.setActive('Y');
			tag.setVerify('Y');
			tag.setCreateUser(userId);
			tag.setName(name);
			tagWriteDao.insert(tag);
			return tag;
		}

	}

	@Override
	public Tag getByName(String name) {
		return tagReadDao.getByName(name);
	}
}

package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.SectorService;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.company.CompanySectorReadDao;
import com.tsb.dao.read.company.SectorReadDao;
import com.tsb.dao.write.company.CompanySectorWriteDao;
import com.tsb.model.company.CompanySector;
import com.tsb.model.company.Sector;


@SuppressWarnings("rawtypes")
@Service
public class SectorServiceImpl implements SectorService {

	@Autowired
	private SectorReadDao sectorReadDao;

	@Autowired
	private CompanySectorReadDao companySectorReadDao;

	@Autowired
	private CompanySectorWriteDao companySectorWriteDao;

	@Override
	public List<Sector> get() {
		return sectorReadDao.get();
	}

	@Override
	public List<Sector> get(Integer id) {
		return sectorReadDao.getByParentId(id);
	}

	@Override
	public List<Sector> getByCompanyId(Integer companyId) {
		List<CompanySector> companySectors = companySectorReadDao.get(companyId);
		List<Sector> sectors = new ArrayList<Sector>();
		for (CompanySector cs : companySectors) {
			Sector sector = sectorReadDao.getById(cs.getSectorId());
			sectors.add(sector);
		}
		return sectors;
	}

	@Override
	public void addCompanySector(Integer companyId, List sectorIds, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		if (sectorIds == null) {
			return;
		} else if (sectorIds.size() == 1) {
			Integer sectorId = (Integer) sectorIds.get(0);
			addCompanySector(sectorId, companyId, userId, time);

		} else if (sectorIds.size() == 2) {
			Integer sectorId = (Integer) sectorIds.get(0);
			addCompanySector(sectorId, companyId, userId, time);
			Integer secondSectorId = (Integer) sectorIds.get(1);
			if (null != secondSectorId) {
				addCompanySector(secondSectorId, companyId, userId, time);
			}
		}
	}

	protected void addCompanySector(Integer sectorId, Integer companyId, Integer userId, Timestamp time) {
		// company_sector
		CompanySector companySector = new CompanySector();
		companySector.setCompanyId(companyId);
		companySector.setSectorId(sectorId);
		companySector.setActive('Y');
		companySector.setCreateTime(time);
		companySector.setVerify('Y');
		companySector.setCreateUser(userId);
		companySectorWriteDao.insert(companySector);
	}

	@Override
	public void updateCompanySector(List<Integer> sectorIds, Integer companyId, Integer userId) {
		List result = companySectorReadDao.get(companyId);
		if (result.size() > 0) {
			companySectorWriteDao.delete(companyId);
		}

		for (Integer id : sectorIds) {
			Timestamp time = new Timestamp(System.currentTimeMillis());
			CompanySector companySector = new CompanySector();
			companySector.setCompanyId(companyId);
			companySector.setSectorId(id);
			companySector.setActive('Y');
			companySector.setCreateTime(time);
			companySector.setVerify('Y');
			companySector.setCreateUser(userId);

			companySectorWriteDao.insert(companySector);
		}
	}

	@Override
	public Sector updateSector(Integer companyId, Integer sectorId, Integer oldId,
			Integer userId) {
		if(oldId != null){
			companySectorWriteDao.deleteOneSector(companyId, oldId);
		}
		Timestamp time = new Timestamp(System.currentTimeMillis());
		CompanySector companySector = new CompanySector();
		companySector.setCompanyId(companyId);
		companySector.setSectorId(sectorId);
		companySector.setActive('Y');
		companySector.setCreateTime(time);
		companySector.setVerify('Y');
		companySector.setCreateUser(userId);

		companySectorWriteDao.insert(companySector);
		
//		companySector =  companySectorReadDao.getBySectorId(companyId, sectorId);
		Sector sector = sectorReadDao.getById(companySector.getSectorId());
		
		List<CompanySector> list = companySectorReadDao.get(companyId);
		for(CompanySector cs : list){
			if(cs.getSectorId() == sector.getParentId()){
				cs.setVerify('Y');
				cs.setModifyUser(userId);
				companySectorWriteDao.update(cs);
			}
		}
		
		return sector;
	}

}

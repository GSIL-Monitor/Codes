package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Footprint;

public interface FootprintReadDao {
List<Footprint> getByCompanyId(Integer companyId);
}

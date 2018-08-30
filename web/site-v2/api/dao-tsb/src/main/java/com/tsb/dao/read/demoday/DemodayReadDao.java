package com.tsb.dao.read.demoday;

import java.util.List;

import com.tsb.model.demoday.Demoday;

public interface DemodayReadDao {
	Demoday get(Integer demodayId);

	Demoday getByName(String name);

	List<Demoday> getAll();
}

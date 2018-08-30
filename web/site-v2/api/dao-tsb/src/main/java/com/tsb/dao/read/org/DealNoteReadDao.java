package com.tsb.dao.read.org;

import java.util.List;

import com.tsb.model.org.user.DealNote;

public interface DealNoteReadDao {
	DealNote get(Integer id);

	List<DealNote> getDealNotes(Integer dealId);
}

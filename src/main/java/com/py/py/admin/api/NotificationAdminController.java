package com.py.py.admin.api;

import java.security.Principal;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Profile;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.py.py.constants.APIAdminUrls;
import com.py.py.constants.ParamNames;
import com.py.py.constants.PathVariables;
import com.py.py.dto.APIPagedResponse;
import com.py.py.dto.DTO;
import com.py.py.dto.out.NotificationDTO;
import com.py.py.service.EventService;
import com.py.py.service.constants.AdminPermissionNames;
import com.py.py.service.constants.ProfileNames;

@Controller
@Profile({ProfileNames.ADMIN})
public class NotificationAdminController extends BaseAdminController {

	@Autowired
	protected EventService eventService;
	
	@PreAuthorize("hasAuthority('" + AdminPermissionNames.ADMIN_NOTIFICATIONS_VIEW + "')")
	@ResponseBody
	@RequestMapping(value = APIAdminUrls.ADMIN_NOTIFICATIONS, method = RequestMethod.GET)
	public APIPagedResponse<DTO, NotificationDTO> notifications(Principal p,
				@PathVariable(PathVariables.ADMIN_TARGET_ID) String atid,
				@RequestParam(value = ParamNames.PAGE, required = false) Integer page,
				@RequestParam(value = ParamNames.SIZE, required = false) Integer size,
				@RequestParam(value = ParamNames.EVENT, required = false) List<String> notification)
						throws Exception {
		Pageable pageable = constructPageable(page, size);
		Page<NotificationDTO> dtos = eventService.getNotificationDTOs(getUserId(p, atid), 
				constructEventTypes(notification), pageable);
		return Success(dtos);
	}
}

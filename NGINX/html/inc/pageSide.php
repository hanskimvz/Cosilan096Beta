<?PHP
$ex_page = explode("/", $_SERVER['DOCUMENT_URI']);
$page = array_pop($ex_page);
$msg= q_language($page); // index.php, admin.php
// $unused= ['account', 'devicetree', 'camera', 'counterlabel', 'database', 'language', 'messagesetup', 'system', 'basic', 'sidemenu', 'dashboardconfig', 'analysis', 'webconfig'];
// foreach($unused as $unused  ){
// 	if (!isset($msg[$unused ])) {
// 		$msg[$unused ] = $unused ;
// 	}
// }



$TITLE_BAR = <<<EOBLOCK
<a class="sidebar-brand" href="/"><img src = "$_TITLE_LOGO" height="26px"><span class="align-middle ml-2">$_DOCUMENT_TITLE</span></a>
EOBLOCK;

// $sq = "select flag, name from ".$_SESSION['db_name'].".webpage_config where page='sidemenu'";
// $rs = mysqli_query($connect0, $sq);
// while($rows = mysqli_fetch_row($rs)){
// 	$flag[$rows[1]] = $rows[0];
// }

function sidebarMenu($id, $href='', $icon='', $label='', $w_name='')
{
	if ($icon){
		$icon = strncmp($icon, 'fa-',3) == 0 ? '<i class="align-middle mr-2 fas fa-fw '.$icon.'"></i>' : '<i class="align-middle" data-feather="'.$icon.'"></i>' ;
	}
	if ($w_name){
		$w_name = 'target="'.$w_name.'"';
	}
	if ($id == -1) {
		return '</ul></li>';
	}
	if ($id == 'split_line') {
		return '<li class="sidebar-header">'.$label.'</li>';
	}
	if (strpos(" ".$href, "#") == 1) {
		return '<li class="sidebar-item"><a href="'.$href.'" data-toggle="collapse" class="sidebar-link collapsed">'.$icon.'<span class="align-middle">'.$label.'</span></a><ul id="'.$id.'" class="sidebar-dropdown list-unstyled collapse">';
	}
	return '<li id="'.$id.'" class="sidebar-item"><a class="sidebar-link" href="'.$href.'" '.$w_name.'>'.$icon.'<span class="align-middle">'.$label.'</span></a></li>';
}

if (file_exists($ROOT_DIR."/NGINX/html/release.json")){
	// print "file exist";
	$json_str = file_get_contents($ROOT_DIR."/NGINX/html/release.json");
	$arr = json_decode($json_str, true);
	foreach($arr['disabled_menu'] as $P => $ids){
		foreach($ids as $id){
			$sq = "update ".$DB_CUSTOM['web_config']." set flag = 'n' where page='".$P."' and body like '%\"id\":\"".$id."\"%' " ;
			$rs = mysqli_query($connect0, $sq);
		}
	}
	foreach($arr['enabled_menu'] as $P => $ids){
		foreach($ids as $id){
			$sq = "update ".$DB_CUSTOM['web_config']." set flag = 'y' where page='".$P."' and body like '%\"id\":\"".$id."\"%' " ;
			$rs = mysqli_query($connect0, $sq);
		}
	}

}

function getMenuFromJson(){
	global $ROOT_DIR;
	global $DB_CUSTOM;
	global $connect0;

	if (!file_exists($ROOT_DIR."/bin/menu.json")){
		return false;
	}
	$json_str = file_get_contents($ROOT_DIR."/bin/menu.json");
	$arr = json_decode($json_str, true);

	for($i=0; $i<sizeof($arr); $i++){
		$sq = "select pk from ".$DB_CUSTOM['web_config']." where page='".$arr[$i]['page']."' and frame='".$arr[$i]['frame']."' and depth=".$arr[$i]['depth']." and pos_x=".$arr[$i]['pos_x']." and pos_y=".$arr[$i]['pos_y']."";
		// print $sq."<br>\n";
		$rs = mysqli_query($connect0, $sq);
		if(!$rs->num_rows){
			$body_str = (json_encode($arr[$i]['body']));
			$sq = "insert into ".$DB_CUSTOM['web_config']."(page, frame, depth, pos_x, pos_y, body, flag) ".
				"values('".$arr[$i]['page']."', '".$arr[$i]['frame']."', ".$arr[$i]['depth'].", ".$arr[$i]['pos_x'].", ".$arr[$i]['pos_y'].", '".$body_str."', '".$arr[$i]['flag']."')";
			// print $sq."";
			$rs = mysqli_query($connect0, $sq);
			// if($rs) {
			// 	print "OK<br>";
			// }
			// else {
			// 	print "Fail<br>";
			// }
		}
	}
}
if (isset($_GET['update_menu'])) {
	getMenuFromJson();
}

$menu_str = "";
$y=0;
if($page == 'index.php'){
	$sq = "select * from ".$DB_CUSTOM['web_config']." where page='main_menu' order by pos_x, pos_y";
}
else if($page == "admin.php") {
	$sq = "select * from ".$DB_CUSTOM['web_config']." where page='admin_menu' order by pos_x, pos_y";
}

$rs = mysqli_query($connect0, $sq);
while($assoc = mysqli_fetch_assoc($rs)){
	if ( $assoc['flag'] == 'n'){
		continue;
	}
	$arr = json_decode($assoc['body'], true);
	if  ($assoc['pos_y'] == 0 && $y) {
		$menu_str  .= sidebarMenu(-1);	
	}
	if (!isset($msg[$arr['lang_key']])) {
		$msg[$arr['lang_key']] = $arr['lang_key'];
	}
	$menu_str  .= "\n".sidebarMenu($arr['id'], $arr['href'], $arr['icon'], $msg[$arr['lang_key']]);
	$y = $assoc['pos_y'];

}
$pageSide = <<<EOPAGE
<nav class="sidebar sidebar-sticky">
	<div class="sidebar-content ">
		$TITLE_BAR 
		<ul class="sidebar-nav">
			$menu_str
		</ul>
	</div>
</nav>
EOPAGE;



// getMenuFromJson();

// $sq = "select * from cnt_demo.webpage_config where page='main_menu' or page='admin_menu'";
// print $sq;
// $rs = mysqli_query($connect0, $sq);
// while ($assoc = mysqli_fetch_assoc($rs)){
// 	$arr = json_decode($assoc['body'], true);
// 	print_r($arr);
// 	$sq = "update cnt_demo.webpage_config set frame='".$arr['id']."' where pk=".$assoc['pk'];
// 	print($sq);
// 	$rsa = mysqli_query($connect0, $sq);
// 	print(",".$rsa);
// }

#### MAIN PAGE SUB MENU ####
// $web_config = [
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>0, "pos_y"=>0, "body"=>'{"id":"split_line", "href": "", "icon":"", "lang_key":"Main"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>1, "pos_y"=>0, "body"=>'{"id":"dashboard", "href": "/?fr=dashboard", "icon":"monitor", "lang_key":"dashboard"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>0, "body"=>'{"id":"footfall", "href": "#footfall", "icon":"users", "lang_key":"footfall"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>1, "body"=>'{"id":"dataGlunt", "href": "/?fr=dataGlunt", "icon":"", "lang_key":"dataglunt"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>2, "body"=>'{"id":"latestFlow", "href": "/?fr=latestFlow", "icon":"", "lang_key":"latestflow"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>3, "body"=>'{"id":"trendAnalysis", "href": "/?fr=trendAnalysis", "icon":"", "lang_key":"trendanalysis"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>4, "body"=>'{"id":"advancedAnalysis", "href": "/?fr=advancedAnalysis", "icon":"", "lang_key":"advancedanalysis"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>5, "body"=>'{"id":"promotionAnalysis", "href": "/?fr=promotionAnalysis", "icon":"", "lang_key":"promotionanalysis"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>6, "body"=>'{"id":"brandOverview", "href": "/?fr=brandOverview", "icon":"", "lang_key":"brandoverview"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>7, "body"=>'{"id":"weatherAnalysis", "href": "/?fr=weatherAnalysis", "icon":"", "lang_key":"weatheranalysis"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>3, "pos_y"=>0, "body"=>'{"id":"kpi", "href": "/?fr=kpi", "icon":"aperture", "lang_key":"kpioverview"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>0, "body"=>'{"id":"dataCompare", "href": "#dataCompare", "icon":"sliders", "lang_key":"datacompare"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>1, "body"=>'{"id":"compareByTime", "href": "/?fr=compareByTime", "icon":"", "lang_key":"comparebytime"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>2, "body"=>'{"id":"compareByPlace", "href": "/?fr=compareByPlace", "icon":"", "lang_key":"comparebyplace"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>3, "body"=>'{"id":"trafficDistribution", "href": "/?fr=trafficDistribution", "icon":"", "lang_key":"trafficdistribution"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>4, "body"=>'{"id":"compareByLabel", "href": "/?fr=compareByLabel", "icon":"", "lang_key":"comparebylabel"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>5, "pos_y"=>0, "body"=>'{"id":"heatmap", "href": "/?fr=heatmap", "icon":"map-pin", "lang_key":"heatmap"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>6, "pos_y"=>0, "body"=>'{"id":"agegender", "href": "/?fr=agegender", "icon":"slack", "lang_key":"genderandage"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>7, "pos_y"=>0, "body"=>'{"id":"macsniff", "href": "/?fr=macsniff", "icon":"wifi", "lang_key":"macsniff"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>0, "body"=>'{"id":"report", "href": "#report", "icon":"book-open", "lang_key":"report"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>1, "body"=>'{"id":"summary", "href": "/?fr=summary", "icon":"", "lang_key":"summary"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>2, "body"=>'{"id":"standard", "href": "/?fr=standard", "icon":"", "lang_key":"standard"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>3, "body"=>'{"id":"premium", "href": "/?fr=premium", "icon":"", "lang_key":"premium"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>4, "body"=>'{"id":"export", "href": "/?fr=export", "icon":"", "lang_key":"export"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>9, "pos_y"=>0, "body"=>'{"id":"split_line", "href": "", "icon":"", "lang_key":"setting"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>10, "pos_y"=>0, "body"=>'{"id":"sensors", "href": "/?fr=sensors", "icon":"camera", "lang_key":"sensors"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>11, "pos_y"=>0, "body"=>'{"id":"sitemap", "href": "/?fr=sitemap", "icon":"map", "lang_key":"sitemap"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>12, "pos_y"=>0, "body"=>'{"id":"split_line", "href": "", "icon":"", "lang_key":"about"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>13, "pos_y"=>0, "body"=>'{"id":"version", "href": "/?fr=version", "icon":"pen-tool", "lang_key":"version"}', "flag"=>"y"],
// 	["page"=>"main_menu", "depth"=>0, "pos_x"=>14, "pos_y"=>0, "body"=>'{"id":"feedback", "href": "/?fr=feedback", "icon":"phone-call", "lang_key":"feedback"}', "flag"=>"y"],

// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>0, "pos_y"=>0, "body"=>'{"id":"account", "href": "./admin.php?fr=account", "icon":"fa-id-card", "lang_key":"account"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>1, "pos_y"=>0, "body"=>'{"id":"device_tree", "href": "./admin.php?fr=device_tree", "icon":"fa-sitemap", "lang_key":"devicetree"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>2, "pos_y"=>0, "body"=>'{"id":"list_device", "href": "./admin.php?fr=list_device", "icon":"fa-camera", "lang_key":"camera"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>3, "pos_y"=>0, "body"=>'{"id":"counter_label_set", "href": "./admin.php?fr=counter_label_set", "icon":"fa-clock", "lang_key":"counterlabel"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>0, "body"=>'{"id":"database", "href": "#database", "icon":"fa-database", "lang_key":"database"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>1, "body"=>'{"id":"split_line", "href": "", "icon":"", "lang_key":"Custom DB"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>2, "body"=>'{"id":"counting", "href": "./admin.php?fr=database&db=counting", "icon":"fa-user-plus", "lang_key":"Counting"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>3, "body"=>'{"id":"agegender", "href": "./admin.php?fr=database&db=agegender", "icon":"fa-venus-mars", "lang_key":"Age Gender"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>4, "body"=>'{"id":"heatmap", "href": "./admin.php?fr=database&db=heatmap", "icon":"fa-street-view", "lang_key":"Heatmap"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>5, "body"=>'{"id":"weather", "href": "./admin.php?fr=database&db=weather", "icon":"fa-cogs", "lang_key":"Weather"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>6, "body"=>'{"id":"split_line", "href": "", "icon":"", "lang_key":"Common DB"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>7, "body"=>'{"id":"params", "href": "./admin.php?fr=database&db=params", "icon":"fa-cogs", "lang_key":"params"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>8, "body"=>'{"id":"counting_common", "href": "./admin.php?fr=database&db=counting_common", "icon":"fa-user-plus", "lang_key":"Counting"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>9, "body"=>'{"id":"event_counting_common", "href": "./admin.php?fr=database&db=event_counting_common", "icon":"fa-user-plus", "lang_key":"EventCounting"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>10, "body"=>'{"id":"face_thumbnail", "href": "./admin.php?fr=database&db=face_thumbnail", "icon":"fa-smile", "lang_key":"Face"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>11, "body"=>'{"id":"heatmap_common", "href": "./admin.php?fr=database&db=heatmap_common", "icon":"fa-street-view", "lang_key":"Heatmap"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>12, "body"=>'{"id":"snapshot", "href": "./admin.php?fr=database&db=snapshot", "icon":"fa-film", "lang_key":"Snapshot"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>13, "body"=>'{"id":"sniff", "href": "./admin.php?fr=database&db=sniff", "icon":"fa-cogs", "lang_key":"MacSniff"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>4, "pos_y"=>14, "body"=>'{"id":"access_log", "href": "./admin.php?fr=database&db=access_log", "icon":"fa-list-ol", "lang_key":"Access Log"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>5, "pos_y"=>0, "body"=>'{"id":"language", "href": "./admin.php?fr=language", "icon":"fa-language", "lang_key":"language"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>6, "pos_y"=>0, "body"=>'{"id":"message_setup", "href": "./admin.php?fr=message_setup", "icon":"fa-comment-alt", "lang_key":"messagesetup"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>7, "pos_y"=>0, "body"=>'{"id":"system", "href": "./admin.php?fr=system", "icon":"settings", "lang_key":"system"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>0, "body"=>'{"id":"webpageConfig", "href": "#webpageConfig", "icon":"file-text", "lang_key":"webconfig"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>1, "body"=>'{"id":"basic", "href": "./admin.php?fr=webpageConfig&db=basic", "icon":"", "lang_key":"basic"}', "flag"=>"y"],
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>2, "body"=>'{"id":"sidemenu", "href": "./admin.php?fr=webpageConfig&db=sidemenu", "icon":"", "lang_key":"sidemenu"}', "flag"=>"y"],	
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>3, "body"=>'{"id":"dashboard", "href": "./admin.php?fr=webpageConfig&db=dashboard", "icon":"", "lang_key":"dashboardconfig"}', "flag"=>"y"],	
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>4, "body"=>'{"id":"analysis", "href": "./admin.php?fr=webpageConfig&db=analysis", "icon":"", "lang_key":"analysis"}', "flag"=>"y"],	
// 	["page"=>"admin_menu", "depth"=>0, "pos_x"=>8, "pos_y"=>5, "body"=>'{"id":"report", "href": "./admin.php?fr=webpageConfig&db=report", "icon":"", "lang_key":"report"}', "flag"=>"y"],	

// ];


// $xxx = (json_encode($web_config, JSON_PRETTY_PRINT));
// $xxx =  str_replace('\"', '"', $xxx);
// $xxx =  str_replace('"\\', '"', $xxx);
// $xxx =  str_replace('"{', '{', $xxx);
// $xxx =  str_replace('}"', '}', $xxx);
// // print($xxx);

// $arx = json_decode($xxx, true);
// // print_r($arx);

// $xxx = (json_encode($arx, JSON_PRETTY_PRINT));
// print($xxx);
// for ($i=0; $i<sizeof($web_config); $i++){
// 	$sq = "insert into cnt_demo.webpage_config(name, page, depth, pos_x, pos_y, body, flag) ".
// 	"values('', '".$web_config[$i]['page']."', ".$web_config[$i]['depth'].", ".$web_config[$i]['pos_x'].", ".$web_config[$i]['pos_y'].", '".$web_config[$i]['body']."', '".$web_config[$i]['flag']."');";

// 	print $sq."\n";

// }

// foreach($web_config as $cfg){
// 	// print_r($cfg);
// 	$arr = json_decode($cfg['body'], true);
// 	if  ($cfg['pos_y'] == 0 && $y) {
// 		$menu_str  .= sidebarMenu(-1);	
// 	}
// 	$menu_str  .= "\n".sidebarMenu($arr['id'], $arr['href'], $arr['icon'], $msg[$arr['lang_key']]);
// 	$y = $cfg['pos_y'];
// }
// print ($menu_str);


// if($page == 'index.phpxxx') {
// 	if(!$_GET['fr']) {
// 		$_GET['fr'] = "dashboard";
// 	}
// 	$menuTag['dashboard'] = $flag['dashboard'] == 'y' ? sidebarMenu('dashboard', './?fr=dashboard', 'monitor',$msg['dashboard']) : '';

// 	if ($flag['footfall'] == 'y'){
// 		$menuTag['footfall'] = '';
// 		$menuTag['footfall'] .= $flag['dataGlunt'] =='y' ? sidebarMenu('dataGlunt', './?fr=dataGlunt', '', $msg['dataglunt']) : '';
// 		$menuTag['footfall'] .= $flag['latestFlow'] =='y' ? sidebarMenu('latestFlow', './?fr=latestFlow', '', $msg['latestflow']) : '';
// 		$menuTag['footfall'] .= $flag['trendAnalysis'] =='y' ? sidebarMenu('trendAnalysis', './?fr=trendAnalysis', '', $msg['trendanalysis']) : ''; 
// 		$menuTag['footfall'] .= $flag['advancedAnalysis'] =='y' ? sidebarMenu('advancedAnalysis', './?fr=advancedAnalysis', '', $msg['advancedanalysis']) : '';
// 		$menuTag['footfall'] .= $flag['promotionAnalysis'] =='y' ? sidebarMenu('promotionAnalysis', './?fr=promotionAnalysis', '', $msg['promotionanalysis'].'(Beta)') : '';
// 		$menuTag['footfall'] .= $flag['brandOverview'] =='y' ? sidebarMenu('brandOverview', './?fr=brandOverview', '', $msg['brandoverview'].'(Beta)') : '';
// 		$menuTag['footfall'] .= $flag['weatherAnalysis'] =='y' ? sidebarMenu('weatherAnalysis', './?fr=weatherAnalysis', '', $msg['weatheranalysis'].'(Beta)') : '';
// 		$menuTag['footfall'] = '<li class="sidebar-item">
// 			<a href="#footfall" data-toggle="collapse" class="sidebar-link collapsed"><i class="align-middle" data-feather="users"></i> <span class="align-middle">'.$msg['footfall'].'</span></a>
// 			<ul id="footfall" class="sidebar-dropdown list-unstyled collapse">'.$menuTag['footfall'].'</ul></li>';
// 	}
	
// 	$menuTag['kpi'] =  $flag['kpi'] == 'y' ? sidebarMenu('kpi', './?fr=kpi', 'aperture', $msg['kpioverview'].'(Beta)') : '' ;
	
// 	if ($flag['dataCompare'] == 'y'){
// 		$menuTag['dataCompare'] = '';
// 		$menuTag['dataCompare'] .= $flag['compareByTime'] == 'y'? sidebarMenu('compareByTime', './?fr=compareByTime', '', $msg['comparebytime']) : '' ;
// 		$menuTag['dataCompare'] .= $flag['compareByPlace'] == 'y' ? sidebarMenu('compareByPlace', './?fr=compareByPlace', '', $msg['comparebyplace']) : '' ;
// 		$menuTag['dataCompare'] .= $flag['trafficDistribution'] == 'y'? sidebarMenu('trafficDistribution', './?fr=trafficDistribution', '', $msg['trafficdistribution']) : '' ;
// 		$menuTag['dataCompare'] .= $flag['compareByLabel'] == 'y'? sidebarMenu('compareByLabel', './?fr=compareByLabel', '', $msg['comparebylabel']) : '' ;
	
// 		$menuTag['dataCompare'] = '<li class="sidebar-item">
// 			<a href="#dataCompare" data-toggle="collapse" class="sidebar-link collapsed"><i class="align-middle" data-feather="sliders"></i><span class="align-middle">'.$msg['datacompare'].'</span></a>
// 			<ul id="dataCompare" class="sidebar-dropdown list-unstyled collapse">'.$menuTag['dataCompare'].'</ul>
// 		</li>';
// 	}
	
// 	$menuTag['heatmap'] = $flag['heatmap'] == 'y' ? sidebarMenu('heatmap', './?fr=heatmap', 'map-pin', $msg['heatmap']) : '';
// 	$menuTag['agegender'] = $flag['agegender'] == 'y' ? sidebarMenu('agegender', './?fr=agegender', 'slack', $msg['genderandage']) : '';
// 	$menuTag['macsniff'] = $flag['macsniff'] == 'y' ? sidebarMenu('macsniff', './?fr=macsniff', 'wifi', $msg['macsniff'].'(Beta)') : ''; 
	
// 	if ($flag['report'] == 'y') {
// 		$menuTag['report']= '';
// 		$menuTag['report'] .= $flag['summary'] == 'y' ? sidebarMenu('summary', './?fr=summary', '', $msg['summary']) : '';
// 		$menuTag['report'] .= $flag['standard'] == 'y' ? sidebarMenu('standard', './?fr=standard', '', $msg['standard']) : '';
// 		$menuTag['report'] .= $flag['premium'] == 'y' ? sidebarMenu('premium', './?fr=premium', '', $msg['premium']) : '';
// 		$menuTag['report'] .= $flag['export'] == 'y' ? sidebarMenu('export', './?fr=export', '', $msg['export']) : '';
	
// 		$menuTag['report'] = '<li class="sidebar-item">
// 			<a href="#report" data-toggle="collapse" class="sidebar-link collapsed"><i class="align-middle" data-feather="book-open"></i> <span class="align-middle">'.$msg['report'].'</span></a>
// 			<ul id="report" class="sidebar-dropdown list-unstyled collapse">'.$menuTag['report'].'</ul>
// 		</li>';
// 	}
	
// 	$menuTag['sensors'] = $flag['sensors'] == 'y' ? sidebarMenu('sensors', './?fr=sensors', 'camera', $msg['sensors']) : ''; 
// 	$menuTag['sitemap'] = $flag['sitemap'] == 'y' ? sidebarMenu('sitemap', './?fr=sitemap', 'map', $msg['sitemap']) : ''; 
// 	$menuTag['version'] = $flag['version'] == 'y' ? sidebarMenu('version', './?fr=version', 'pen-tool', $msg['version']) :'';
// 	$menuTag['feedback'] = $flag['feedback'] == 'y' ? sidebarMenu('feedback', './?fr=feedback', 'phone-call', $msg['feedback'].'(Beta)') : '';

// 	$pageSide = <<<EOPAGE
// 	<nav class="sidebar sidebar-sticky">
// 		<div class="sidebar-content ">
// 			$TITLE_BAR 
// 			<ul class="sidebar-nav">
// 				<li class="sidebar-header">Main</li>
// 				$menuTag[dashboard]
// 				$menuTag[footfall]
// 				$menuTag[kpi]
// 				$menuTag[dataCompare]
// 				$menuTag[heatmap]
// 				$menuTag[agegender]
// 				$menuTag[macsniff]
// 				$menuTag[report]
// 				<li class="sidebar-header">Setting</li>
// 				$menuTag[sensors]
// 				$menuTag[sitemap]
// 				<li class="sidebar-header">About</li>
// 				$menuTag[version]
// 				$menuTag[feedback]

// 			</ul>
// 		</div>
// 	</nav>
// EOPAGE;
// }

// else if($page == 'main2.php') {
// 	$msg= q_language("index.php");
// 	if(!$_GET['fr']) {
// 		$_GET['fr'] = "dashboard";
// 	}
// 	$pageSide = <<<EOPAGE
// 	<nav class="sidebar sidebar-sticky">
// 		<div class="sidebar-content ">
// 			$TITLE_BAR 
// 			<ul class="sidebar-nav">
// 				<li class="sidebar-header">Main</li>
// 				$menuTag[dashboard]
// 				$menuTag[footfall]
// 				$menuTag[kpi]
// 				$menuTag[dataCompare]
// 				$menuTag[heatmap]
// 				$menuTag[agegender]
// 				$menuTag[macsniff]
// 				$menuTag[report]
// 				<li class="sidebar-header">Setting</li>
// 				$menuTag[sensors]
// 				$menuTag[sitemap]
// 				<li class="sidebar-header">About</li>
// 				$menuTag[version]
// 				$menuTag[feedback]

// 			</ul>
// 		</div>
// 	</nav>
// EOPAGE;
// }


// ##### ADMIN PAGE  SUB MENU ##
// else if($page == "admin.php") {
// 	if(!$_GET['fr']) {
// 		$_GET['fr'] = "account";
// 	}
// 	$menuTag['account'] = sidebarMenu('account', './admin.php?fr=account', 'fa-id-card', $msg['account']);
// 	$menuTag['deviceTree'] = sidebarMenu('device_tree', './admin.php?fr=device_tree', 'fa-sitemap', $msg['devicetree']); 
// 	$menuTag['listDevice'] = sidebarMenu('list_device', './admin.php?fr=list_device', 'fa-camera', $msg['camera']);
// 	$menuTag['counterLabel'] = sidebarMenu('counter_label_set', './admin.php?fr=counter_label_set', 'fa-clock', $msg['counterlabel']);
	
// 	$menuTag['database']  = '<li class="sidebar-header">Custom DB</li>';
// 	$menuTag['database'] .= sidebarMenu('counting', './admin.php?fr=database&db=counting', 'fa-user-plus', 'Counting');
// 	$menuTag['database'] .= sidebarMenu('agegender', './admin.php?fr=database&db=agegender', 'fa-venus-mars', 'Age Gender');
// 	$menuTag['database'] .= sidebarMenu('heatmap', './admin.php?fr=database&db=heatmap', 'fa-street-view', 'Heatmap');
// 	$menuTag['database'] .= sidebarMenu('weather', './admin.php?fr=database&db=weather', 'fa-cogs', 'Weather');
// 	$menuTag['database'] .= '<li class="sidebar-header">Common DB</li>';
// 	$menuTag['database'] .= sidebarMenu('params', './admin.php?fr=database&db=params', 'fa-cogs', 'Parameter');
// 	$menuTag['database'] .= sidebarMenu('counting_common', './admin.php?fr=database&db=counting_common', 'fa-user-plus', 'Counting');
// 	$menuTag['database'] .= sidebarMenu('event_counting_common', './admin.php?fr=database&db=event_counting_common', 'fa-user-plus', 'EventCounting');
// 	$menuTag['database'] .= sidebarMenu('face_thumbnail', './admin.php?fr=database&db=face_thumbnail', 'fa-smile', 'Face');
// 	$menuTag['database'] .= sidebarMenu('heatmap_common', './admin.php?fr=database&db=heatmap_common', 'fa-street-view', 'Heatmap');
// 	$menuTag['database'] .= sidebarMenu('snapshot', './admin.php?fr=database&db=snapshot', 'fa-film', 'Snapshot');
// 	$menuTag['database'] .= sidebarMenu('sniff', './admin.php?fr=database&db=sniff', 'fa-cogs', 'MacSniff');
// 	$menuTag['database'] .= sidebarMenu('access_log', './admin.php?fr=database&db=access_log', 'fa-list-ol', 'Access Log');
	
// 	$menuTag['database'] = '<li class="sidebar-item">
// 		<a href="#database" data-toggle="collapse" class="sidebar-link collapsed"><i class="align-middle mr-2 fas fa-fw fa-database"></i><span class="align-middle">'.$msg['database'].'</span></a>
// 		<ul id="database" class="sidebar-dropdown list-unstyled collapse">'.$menuTag['database'].'</ul>
// 	</li>';
	
// 	$menuTag['language'] = sidebarMenu('language', './admin.php?fr=language', 'fa-language', $msg['language']);
// 	$menuTag['messageSetup'] = sidebarMenu('message_setup', './admin.php?fr=message_setup', 'fa-comment-alt', $msg['messagesetup']);
// 	// $menuTag['system'] = sidebarMenu('system', './inc/system.php?fr=service', 'settings', $msg['system'],'system');
// 	$menuTag['system']= "";
	
// 	$menuTag['webpageConfig']  = sidebarMenu('basic', './admin.php?fr=webpageConfig&db=basic', '', $msg['basic']);
// 	$menuTag['webpageConfig'] .= sidebarMenu('sidemenu', './admin.php?fr=webpageConfig&db=sidemenu', '', $msg['sidemenu']);
// 	$menuTag['webpageConfig'] .= sidebarMenu('dashboard', './admin.php?fr=webpageConfig&db=dashboard', '', $msg['dashboardconfig']);
// 	$menuTag['webpageConfig'] .= sidebarMenu('analysis', './admin.php?fr=webpageConfig&db=analysis', '', $msg['analysis']);
// 	$menuTag['webpageConfig'] .= sidebarMenu('report', './admin.php?fr=webpageConfig&db=report', '', $msg['report']);
// 	$menuTag['webpageConfig'] = '<li class="sidebar-item">
// 		<a href="#webpageConfig" data-toggle="collapse" class="sidebar-link collapsed"><i class="align-middle" data-feather="file-text"></i><span class="align-middle">'.$msg['webconfig'].'</span></a>
// 		<ul id="webpageConfig" class="sidebar-dropdown list-unstyled collapse">'.$menuTag['webpageConfig'].'</ul>
// 	</li>';
		
// 	$pageSide = <<<EOPAGE
// 	<nav class="sidebar sidebar-sticky">
// 		<div class="sidebar-content js-simplebar">
// 			$TITLE_BAR
// 			<ul class="sidebar-nav">
// 				$menuTag[account]
// 				$menuTag[deviceTree]
// 				$menuTag[listDevice]
// 				$menuTag[counterLabel]
// 				$menuTag[database]
// 				$menuTag[language]
// 				$menuTag[messageSetup]
// 				$menuTag[system]
// 				$menuTag[webpageConfig]
// 			</ul>
// 		</div>
// 	</nav>
// EOPAGE;
	
// }
// unset($msg);

?>
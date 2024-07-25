import {
  _decorator,
  Component,
  Prefab,
  Label,
  Button,
  instantiate,
  Node,
  Layout,
  Animation,
  Canvas,
  UITransform,
} from "cc";
import GlobalState from "../../state/GlobalState";
import { TopReferralRecord } from "./top_referral_record";
import { TrophySection } from "../trophy_section";
import { CurrentUserReferralRecord } from "./current_user_referral_record";
import ApiClient from "../../api/ApiClient";

const { ccclass, property } = _decorator;

@ccclass("TopReferralPage")
export class TopReferralPage extends Component {
  @property({ type: Node }) trophySection: Node | null = null;
  @property({ type: Node }) scrollContent: Node | null = null;
  @property({ type: Node }) emptyStateLabel: Node | null = null;

  @property({ type: Node }) bottomPanel: Node | null = null;
  @property({ type: Node }) scrollView: Node | null = null;
  @property({ type: Node }) topRecord: Node | null = null;
  
  @property({ type: Prefab }) topReferralRecord: Prefab | null = null;
  @property({ type: Prefab }) currentUserReferralRecord: Prefab | null = null;
  @property({ type: Prefab }) emptyRecord: Prefab | null = null;

  private leaderboardPage
  private userInfo
  private oldRecordNum: number = 0
  private newRecordNum: number = 0
  private scrollHeightMidpoint: number = 0
  private isLoadingNewPage: boolean = false
  private loadedTopRecord: boolean = false
  private currentUserRecordToTrack: Node = null
  private recordHeight: number = 50
  private currentUserInfo

  onLoad() {
    this.loadTopReferralRecords();
  }

  update() {
    this.updateScrollMidpoint()
    this.preloadPage()
    this.trackCurrentUserRecordPos()
  }
  
  updateScrollMidpoint() {
    // updates the scroll midpoint every time more records are added
    if (this.oldRecordNum != this.newRecordNum) {
      this.oldRecordNum = this.newRecordNum
      this.scrollHeightMidpoint = this.oldRecordNum * this.recordHeight * 0.5
    }
  }

  preloadPage() {
    /*
    if the position of scrollContent is over the combined height of 
    half of the total records: render the new page
    */
    if (this.isLoadingNewPage == false && this.scrollContent.position.y > this.scrollHeightMidpoint) {
      if (this.leaderboardPage["next"]) {
        this.isLoadingNewPage = true
        this.loadNextPage()
      }
    }
  }
  
  trackCurrentUserRecordPos() {
    if (this.currentUserRecordToTrack) {
      let yPos: number = this.currentUserRecordToTrack.getWorldPosition().y
  
      if (yPos >= 0 && yPos < 250) {
        this.hideTopRecord()
      } else {
        this.showTopRecord(this.currentUserInfo)
      }
    }
  }

  async loadTopReferralRecords(): Promise<void> {
    // loading userInfo
    this.userInfo = GlobalState.getUserData();

    if (!this.userInfo) {
      this.userInfo = await GlobalState.loadUserData();
      if (this.userInfo) {
        GlobalState.setUserData(this.userInfo);
      }
    }
  
    // loading leaderboard page and setting top three usernames for trophy section
    if (this.userInfo) {
      this.leaderboardPage = await ApiClient.leaderboards.getPage(
        this.userInfo.telegram_id,
        "referral"
      );

      // render first page and second page if it exists
      this.renderRecords(this.leaderboardPage);
      if (this.leaderboardPage["next"]) {
        this.loadNextPage();
      }

      this.setTopThreeUsernames(this.leaderboardPage);
    } else {
      console.log("Failed to load top referral records.");
    }
  }

  renderRecords(page) {
    let rankings = page["results"]
    let rankingsLen = rankings.length

    // update recordNum
    this.newRecordNum += rankingsLen

    // empty state label when there are no users
    if (rankingsLen > 0) {
      this.emptyStateLabel.active = false;
    } else {
      this.emptyStateLabel.active = true;
      return;
    }

    // load the top record if haven't
    if (!this.loadedTopRecord) {
      this.currentUserInfo = this.findCurrentUser(page)

      this.showTopRecord(this.currentUserInfo)

      if (this.currentUserInfo["rank"] > 5) {
        let newRecord = instantiate(this.emptyRecord);
        this.scrollContent.addChild(newRecord);
      }
    }

    // load records
    this.loadRecords(rankings)
  }

  findCurrentUser(page) {
    for (let i = 0; i < 10; i++) {
      if (page["results"][i]["username"] == this.userInfo.username) {
        return page["results"][i];
      }
      if (!page["results"][i]) break;
    }
    if ("current_user" in page) {
      return page["current_user"];
    }
  }

  // renders the first record (current user record) at the top of the scroll view
  showTopRecord(rank) {
    if (!this.loadedTopRecord && rank) {
      let recordComponent: CurrentUserReferralRecord
      
      recordComponent = this.topRecord.getComponent(CurrentUserReferralRecord);
      recordComponent.init(rank);
      this.loadedTopRecord = true
    }
    this.topRecord.active = true
  }
  
  hideTopRecord() {
    this.topRecord.active = false
  }

  loadRecords(rankings) {
    for (let i = 0; i < 10; i++) {
      if (!rankings[i]) break;

      if (rankings[i].username == this.userInfo.username) {
        this.loadRecord(this.currentUserReferralRecord, rankings[i]);
      } else {
        this.loadRecord(this.topReferralRecord, rankings[i]);
      }
    }
  }
  
  loadRecord(recordType, rank) {
    let newRecord = instantiate(recordType);
    let earnerRecordComponent: CurrentUserReferralRecord | TopReferralRecord

    if (recordType == this.currentUserReferralRecord) {
      earnerRecordComponent = newRecord.getComponent(CurrentUserReferralRecord);
      earnerRecordComponent.init(rank);
    } else if (recordType == this.topReferralRecord) {
      earnerRecordComponent = newRecord.getComponent(TopReferralRecord);
      earnerRecordComponent.init(rank);
    }
    this.scrollContent.addChild(newRecord);

    // assignment for y value tracking of current user earner record
    if (recordType == this.currentUserReferralRecord) {
      this.currentUserRecordToTrack = newRecord
    } 
  }
  
  // loads and renders the next page
  async loadNextPage() {
    let cursor: string
    
    // get the cursor for the next page url
    cursor = (this.leaderboardPage["next"].split("?"))[1];

    this.leaderboardPage = await ApiClient.leaderboards.getOtherPage(
      this.userInfo.telegram_id,
      cursor
    );

    this.renderRecords(this.leaderboardPage);
    this.isLoadingNewPage = false
  }

  setTopThreeUsernames(page) {
    let topThreeUsernames: string[] = [];
    let rankings = page["results"]
    for (let i = 0; i < 3; i++) {
      if (rankings[i]) {
        topThreeUsernames.push(rankings[i].username);
      } else {
        topThreeUsernames.push("-");
      }
    }
    const trophySectionComponent =
      this.trophySection.getComponent(TrophySection);
    if (trophySectionComponent) {
      trophySectionComponent.init(topThreeUsernames);
    }
  }
}

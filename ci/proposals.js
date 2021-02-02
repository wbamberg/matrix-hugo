const path = require('path');
const fs = require('fs');

const fetch = require('node-fetch');

const outputDir = path.join(__dirname, "../data/msc");

const labels = [
  "proposal-in-review",
  "proposed-final-comment-period",
  "final-comment-period",
  "finished-final-comment-period",
  "spec-pr-missing",
  "spec-pr-in-review",
  "merged"
];

//const label = "proposed-final-comment-period"

let issues = [];

async function getAllIssues() {

  function getNextLink(header) {
    const links = header.split(",");
    for (const link of links) {
      const linkPieces = link.split(";");
      if (linkPieces[1] == ` rel=\"next\"`) {
        const next = linkPieces[0].trim();
        return next.substring(1, next.length-1);
      }
    }
    return null;
  }

  let pageLink = "https://api.github.com/repos/matrix-org/matrix-doc/issues?state=all&labels=proposal&per_page=100";
  while (pageLink) {
    const response = await fetch(pageLink);
    const issuesForPage = await response.json();
    issues = issues.concat(issuesForPage);
    const linkHeader = response.headers.get("link");
    pageLink = getNextLink(linkHeader);
  }
}

getAllIssues().then(processIssues);

function getAuthors(issue) {
  const re = /^Author: (.+?)$/m;
  const found = issue.body.match(re);
  if (found) {
    console.log(found[1]);
  }
}

function getShepherd(issue) {
  const re = /^Shepherd: (.+?)$/m;
  const found = issue.body.match(re);
  if (found) {
    console.log(found[1]);
  }
}

function processIssues()  {
  for (const label of labels) {
    let issuesForLabel = issues.filter(msc => {
      return msc.labels.some(l => l.name === label);
    });
    for (const issue of issuesForLabel) {
      getShepherd(issue);
    }
    issuesForLabel = issuesForLabel.map(issue => {
      return {
        number: issue.number,
        url: issue.url,
        title: issue.title,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
        body: issue.body
      }
    });
    const issuesData = JSON.stringify(issuesForLabel, null, '\t');
    const outputFile = path.join(outputDir, `${label}.json`);
    fs.writeFileSync(outputFile, issuesData);
  }
}

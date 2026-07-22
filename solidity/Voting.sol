// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Glasanje o zahtevu za kupovinu/prodaju imovine
/// @notice Deploy-uje se jedna instanca po zahtevu (director-servis to radi
///         iz /decision endpoint-a). uuid zahteva se ne čuva na lancu — vezu
///         između uuid-a i adrese ovog ugovora drži Redis, van lanca.
contract Voting {
    enum Status { Pending, Approved, Rejected }

    mapping(address => bool) public isVoter;
    mapping(address => bool) public hasVoted;
    address[] public voters;

    uint256 public confirmCount;
    uint256 public rejectCount;
    uint256 public immutable requiredVotes; // n/2 + 1

    Status public status;

    event VoteCast(address indexed voter, bool confirmed);
    event VotingConcluded(Status result);

    modifier onlyVoter() {
        require(isVoter[msg.sender], "Invalid address.");
        _;
    }

    modifier votingOpen() {
        require(status == Status.Pending, "Voting ended.");
        _;
    }

    /// @param _voters lista dozvoljenih glasačkih adresa; mora biti neparne
    ///        dužine (ista provera postoji i na /decision endpoint-u pre
    ///        deploy-a, ovde je dupliramo da ugovor bude ispravan i van
    ///        konteksta te aplikacije).
    constructor(address[] memory _voters) {
        require(_voters.length % 2 == 1, "Even number of voters.");

        for (uint256 i = 0; i < _voters.length; i++) {
            address voter = _voters[i];
            require(voter != address(0), "Invalid address.");
            require(!isVoter[voter], "Duplicate voter address.");
            isVoter[voter] = true;
            voters.push(voter);
        }

        requiredVotes = _voters.length / 2 + 1;
        status = Status.Pending;
    }

    /// Poziva se slanjem transakcije iz approve_transaction (iz odgovora
    /// na /decision).
    function approve() external onlyVoter votingOpen {
        _castVote(true);
    }

    /// Poziva se slanjem transakcije iz reject_transaction.
    function reject() external onlyVoter votingOpen {
        _castVote(false);
    }

    function _castVote(bool confirmed) private {
        require(!hasVoted[msg.sender], "Already voted.");
        hasVoted[msg.sender] = true;

        if (confirmed) {
            confirmCount++;
        } else {
            rejectCount++;
        }

        emit VoteCast(msg.sender, confirmed);

        if (confirmCount >= requiredVotes) {
            status = Status.Approved;
            emit VotingConcluded(status);
        } else if (rejectCount >= requiredVotes) {
            status = Status.Rejected;
            emit VotingConcluded(status);
        }
    }

    function voterCount() external view returns (uint256) {
        return voters.length;
    }
}

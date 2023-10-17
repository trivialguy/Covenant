pragma solidity ^0.8.0;

// import "./IERC20.sol";
// import "./SafeERC20.sol";

contract Main{
    function compare(string memory str1, string memory str2) public pure returns (bool) {
        return keccak256(abi.encodePacked(str1)) == keccak256(abi.encodePacked(str2));
    }
    uint256 red=0;
    uint256 blue=0;
    uint256 deno;
    uint256 ind=0;
    address payable admin;
    constructor(uint256 _deno, address payable _admin){
        deno = _deno;
        admin = _admin;
    }
    string[] public arr;
    function deposit() public payable returns (uint256){
        return address(this).balance;
    }
    function arr_length() public view returns (uint256){
        return arr.length;
    }
    function deno_return() public view returns (uint256){
        return deno;
    }
    function curr_length() public view returns (uint256){
        return ind;
    }
    function vote(string calldata has) public payable returns (uint256){
        require(msg.value==deno,"");
        arr.push(has);
        return arr.length;
    }
    function countvote(string calldata vote_A, string calldata vote_B, uint256 i) public{
        // require(msg.sender==admin,"");
        if(compare(arr[i-1],vote_A)) red++;
        else if(compare(arr[i-1],vote_B)) blue++;
    }
    function vote_compare(string calldata vote_A, string calldata vote_B, uint256 i, address payable voter) public{
        // require(msg.sender==admin,"");
        if(red>blue)
        if(compare(arr[i-1],vote_B)) voter.transfer(deno*(red+blue)/blue);
        else if(blue>red)
        if(compare(arr[i-1],vote_A)) voter.transfer(deno*(red+blue)/red);
        ind = i;


    }
    function empty_balance() public{
        require(msg.sender==admin,"");
        admin.transfer(address(this).balance);
    }

}
